#!/usr/bin/env python3
"""Replay the actual timer bug/fix through the task gateway in a NEW isolated copy.
The repair fixture was produced by a separate mainloop agent and reviewed by an
assembly agent. This deterministic replay launches checks, not AI agents.
"""
import argparse
import json
from pathlib import Path
import shutil
from coordination_store import Rejected, file_hash
from task_ops import operate


def validate_flow(source, output, node):
    source=Path(source).resolve();output=Path(output).resolve()
    if output.exists():raise ValueError('Output must not exist; previous runs are never overwritten')
    repo=Path(__file__).resolve().parents[1]
    fixture=json.loads((repo/'scripts/tests/fixtures/timer-repair.json').read_text())
    for item in fixture:
        if (source/item['path']).read_text()!=item['before']:
            raise ValueError('Source no longer matches regression baseline: '+item['path'])
    output.mkdir(parents=True)
    shutil.copytree(source/'src',output/'src',ignore=shutil.ignore_patterns('doc','docs','__pycache__'))
    (output/'tests').mkdir();shutil.copy2(repo/'scripts/tests/helpers/timer_regression.cjs',output/'tests/timer_regression.cjs')
    def put(path,text):
        p=output/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    put('docs/requirements.md','R1: pause/resume preserves elapsed time and frame count; stop/start begins a fresh session.\n')
    put('docs/design/timer.md','D1: verify the existing Timer.stop/start pause/resume delegation before changing the lifecycle contract.\n')
    loop_files=[item['path'] for item in fixture];roles={}
    for role,title,files,mode in [('mainloop','主循环（真实源码回放）',loop_files,'owner'),('assembly','装配（集成回放）',['tests/integration-notes.md'],'integration')]:
        put('role-cards/'+role+'/role-card.md','# '+title+'\n\n仅用于隔离验证，不修改原项目。\n')
        put('role-cards/'+role+'/boundary.md','# Section 1\n\n| Type | Path | Scope |\n| --- | --- | --- |\n'+''.join('| file | `'+f+'` | assigned |\n' for f in files))
        roles[role]={'card':'role-cards/'+role+'/role-card.md','boundary':'role-cards/'+role+'/boundary.md','writeFiles':files,'operations':['repair'],'autoDispatch':True,'checks':{'regression':{'argv':[node,'tests/timer_regression.cjs','--root','.', '--mode',mode],'timeoutSeconds':30}}}
    config={'schemaVersion':1,'roles':roles,'maxConcurrentWorkers':2,'designFiles':['docs/design/timer.md'],'allowDesignRevision':True,'authorizationContext':'Explicitly requested isolated validation; not production authorization.'}
    put('.ans/project.json',json.dumps(config,ensure_ascii=False,indent=2))
    reads=['tests/timer_regression.cjs','src/models/engine.ts','src/pipelines/gameloop/fixed.timestep.ts','src/interface/engine.ts']
    task='timer-pause-resume'
    plan={'schemaVersion':1,'taskId':task,'requirement':{'path':'docs/requirements.md','version':'R1'},'design':{'path':'docs/design/timer.md','version':'D1'},'nodes':[
      {'nodeId':'mainloop-repair','roleId':'mainloop','title':'暂停恢复计时修复','stage':'implementation','operation':'repair','writeSet':loop_files,'readSet':reads,'checks':['regression'],'dependsOn':[]},
      {'nodeId':'assembly-check','roleId':'assembly','title':'真实 Engine 生命周期验收','stage':'integration','operation':'repair','writeSet':['tests/integration-notes.md'],'readSet':reads+loop_files,'checks':['regression'],'dependsOn':[]}]}
    initialized=operate(output,task,'init',{'configPath':'.ans/project.json','approvedConfigSha256':file_hash(output,'.ans/project.json'),'plan':plan})
    coordinator=initialized['coordinatorToken']
    def op(command,request=None):
        request=dict(request or {})
        if command in {'dispatch','revise','verify','recover'}:request['coordinatorToken']=coordinator
        return operate(output,task,command,request)
    def dispatch(stage):
        a=op('dispatch',{'nodeId':stage,'workerId':stage+'-worker'})['assignment'];op('ack',a);return a
    initial={name:dispatch(name) for name in ['mainloop-repair','assembly-check']}
    failed={name:op('run-check',{**a,'checkId':'regression'})['evidence']['exitCode'] for name,a in initial.items()}
    assert all(code!=0 for code in failed.values()),'Original bug must actually fail'
    op('report',{**initial['mainloop-repair'],'reportId':'bug','kind':'issue','summary':'真实 Timer 与 Engine 回归均复现：暂停恢复后累计时间为 0.1 而非 0.2。'})
    put('docs/design/timer.md','D2: explicit Timer.pause/resume retain elapsed time and frames, exclude paused wall time, reset resumed delta. GameLoop delegates pause/resume. stop/start creates a new session. Integration waits for verified mainloop repair.\n')
    op('revise',{'version':'D2','affected':['mainloop-repair'],'dependencies':{'assembly-check':['mainloop-repair']},'reason':'修订生命周期契约，暂停两角色旧批次，先验证主循环再放行集成。'})
    old=op('report',{**initial['assembly-check'],'reportId':'old-D1','kind':'complete','summary':'迟到的 D1 完成反馈'})
    assert old['accepted'] is False
    for a in initial.values():op('stop',{**a,'summary':'旧批次的同步检查进程已退出，释放保留范围。'})
    early_blocked=False
    try:dispatch('assembly-check')
    except Rejected:early_blocked=True
    assert early_blocked
    a=dispatch('mainloop-repair')
    for item in fixture:put(item['path'],item['after'])
    owner=op('run-check',{**a,'checkId':'regression'});assert owner['evidence']['exitCode']==0
    op('report',{**a,'reportId':'D2-owner','kind':'complete','summary':'D2 主循环修复及契约回归通过。','changedPaths':loop_files})
    self_verify_blocked=False
    try:operate(output,task,'verify',{'nodeId':'mainloop-repair',**a})
    except Rejected:self_verify_blocked=True
    assert self_verify_blocked
    op('verify',{'nodeId':'mainloop-repair'})
    b=dispatch('assembly-check')
    put('tests/integration-notes.md','# Integration evidence\nReal GameEngine start/pause/resume/stop wrappers, real DefaultGameLoop and PerformanceTimer, deterministic clock and RAF; initialized scene/render stubs. No DOM/browser startup or TypeScript compiler coverage.\n')
    integration=op('run-check',{**b,'checkId':'regression'});assert integration['evidence']['exitCode']==0
    op('report',{**b,'reportId':'D2-integration','kind':'complete','summary':'真实 Engine 生命周期包装路径集成回归通过。','changedPaths':['tests/integration-notes.md']})
    op('verify',{'nodeId':'assembly-check'})
    current=op('status')['state'];assert all(n['status']=='verified' for n in current['nodes'])
    for item in fixture:assert (source/item['path']).read_text()==item['before'],'Original source changed'
    summary={'project':str(output),'taskId':task,'failedBefore':failed,'passedAfter':{'owner':owner['evidence']['exitCode'],'integration':integration['evidence']['exitCode']},'staleFeedbackRejected':not old['accepted'],'dependentDispatchBlocked':early_blocked,'workerSelfVerificationBlocked':self_verify_blocked,'eventCount':current['lastEventSeq'],'stages':[{k:n[k] for k in ['nodeId','roleId','status','attemptId']} for n in current['nodes']],'limits':'Actual source regression replay; not browser initialization, type checking or OS write sandbox.'}
    put('docs/validation-summary.json',json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--node',required=True)
    a=p.parse_args();print(json.dumps(validate_flow(a.source,a.output,a.node),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
