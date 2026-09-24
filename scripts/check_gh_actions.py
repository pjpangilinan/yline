import urllib.request
import json

url = 'https://api.github.com/repos/pjpangilinan/yline/actions/runs'
req = urllib.request.Request(url, headers={'User-Agent': 'python'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    runs = data.get('workflow_runs', [])
    print(f'Total workflow runs found: {len(runs)}')
    for r in runs[:10]:
        print(f"ID: {r.get('id')} | Name: {r.get('name')} | Status: {r.get('status')} | Conclusion: {r.get('conclusion')}")
        print(f"  URL: {r.get('html_url')}")
        print(f"  Branch: {r.get('head_branch')} | Commit: {r.get('head_sha')[:7]} - {r.get('head_commit', {}).get('message', '').splitlines()[0]}")
        
        # Check jobs
        jobs_url = r.get('jobs_url')
        if jobs_url and r.get('conclusion') == 'failure':
            jreq = urllib.request.Request(jobs_url, headers={'User-Agent': 'python'})
            with urllib.request.urlopen(jreq) as jresp:
                jdata = json.loads(jresp.read().decode())
            for job in jdata.get('jobs', []):
                print(f"    Job: {job.get('name')} | Conclusion: {job.get('conclusion')}")
                for step in job.get('steps', []):
                    if step.get('conclusion') == 'failure':
                        print(f"      FAILED STEP: {step.get('name')}")
except Exception as e:
    print('Error checking GitHub API:', e)
