"""Download public primary sources only; writes exclusively beside this script."""
import concurrent.futures
import hashlib
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parent
SOURCES = {
 'python_asyncio': 'https://docs.python.org/3.12/library/asyncio-task.html',
 'python_queue': 'https://docs.python.org/3.12/library/asyncio-queue.html',
 'python_futures': 'https://docs.python.org/3.12/library/concurrent.futures.html',
 'fastapi_background': 'https://fastapi.tiangolo.com/tutorial/background-tasks/',
 'fastapi_streaming': 'https://fastapi.tiangolo.com/advanced/custom-response/',
 'fastapi_websockets': 'https://fastapi.tiangolo.com/advanced/websockets/',
 'starlette_background': 'https://www.starlette.io/background/',
 'starlette_responses': 'https://www.starlette.io/responses/',
 'pydantic_fields': 'https://docs.pydantic.dev/latest/concepts/fields/',
 'pydantic_strict': 'https://docs.pydantic.dev/latest/concepts/strict_mode/',
 'docker_depends': 'https://docs.docker.com/compose/how-tos/startup-order/',
 'docker_volumes': 'https://docs.docker.com/engine/storage/volumes/',
 'docker_bind': 'https://docs.docker.com/engine/storage/bind-mounts/',
 'qdrant_collections': 'https://qdrant.tech/documentation/concepts/collections/',
 'qdrant_filtering': 'https://qdrant.tech/documentation/concepts/filtering/',
 'pgvector_readme': 'https://raw.githubusercontent.com/pgvector/pgvector/master/README.md',
 'redis_persistence': 'https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/',
 'postgres_indexes': 'https://www.postgresql.org/docs/17/indexes-types.html',
 'sqlite_wal': 'https://www.sqlite.org/wal.html',
 'httpx_async': 'https://www.python-httpx.org/async/',
 'requests_advanced': 'https://requests.readthedocs.io/en/latest/user/advanced/',
 'flask_async': 'https://flask.palletsprojects.com/en/stable/async-await/',
 'celery_tasks': 'https://docs.celeryq.dev/en/stable/userguide/tasks.html',
 'requests_async_readme': 'https://raw.githubusercontent.com/encode/requests-async/master/README.md',
 'langgraph_readme': 'https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md',
 'crewai_readme': 'https://raw.githubusercontent.com/crewAIInc/crewAI/main/README.md',
 'browser_readme': 'https://raw.githubusercontent.com/browser-use/browser-use/main/README.md',
 'pydantic_ai_readme': 'https://raw.githubusercontent.com/pydantic/pydantic-ai/main/README.md',
}
REPOS = {
 'langgraph':'langchain-ai/langgraph', 'qdrant':'qdrant/qdrant',
 'browser':'browser-use/browser-use', 'fastapi':'fastapi/fastapi',
 'pydantic':'pydantic/pydantic', 'pgvector':'pgvector/pgvector',
 'httpx':'encode/httpx','crewai':'crewAIInc/crewAI',
 'pydantic_ai':'pydantic/pydantic-ai','celery':'celery/celery',
 'requests_async':'encode/requests-async', 'autogpt_plugins':'Significant-Gravitas/Auto-GPT-Plugins',
 'awesome_python':'vinta/awesome-python', 'awesome':'sindresorhus/awesome',
 'old_fastapi':'tiangolo/fastapi', 'old_langchain':'hwchase17/langchain',
}
for key, repo in REPOS.items():
 SOURCES['repo_'+key] = 'https://api.github.com/repos/'+repo
for key in ['langgraph','qdrant','browser','fastapi','pydantic','pgvector','httpx','crewai','pydantic_ai','celery','awesome_python','awesome']:
 SOURCES['releases_'+key] = 'https://api.github.com/repos/'+REPOS[key]+'/releases?per_page=10'
SOURCES['issues_httpx'] = 'https://api.github.com/repos/encode/httpx/issues?state=closed&labels=bug&sort=updated&direction=desc&per_page=10'

SOURCES.update({
 'python_queue_313': 'https://docs.python.org/3.13/library/asyncio-queue.html',
 'browser_pyproject': 'https://raw.githubusercontent.com/browser-use/browser-use/main/pyproject.toml',
 'pgvector_license': 'https://raw.githubusercontent.com/pgvector/pgvector/master/LICENSE',
 'pgvector_tags': 'https://api.github.com/repos/pgvector/pgvector/tags?per_page=10',
 'pydantic_ai_mcp': 'https://ai.pydantic.dev/mcp/overview/',
 'crewai_mcp': 'https://docs.crewai.com/en/mcp/overview',
 'langgraph_persistence': 'https://docs.langchain.com/oss/python/langgraph/persistence',
})
for key in ['browser','pydantic','crewai','qdrant','httpx','fastapi','celery','pydantic_ai']:
 SOURCES['latest_'+key] = 'https://api.github.com/repos/'+REPOS[key]+'/releases/latest'

class Text(HTMLParser):
 def __init__(self): super().__init__(); self.parts=[]; self.skip=0
 def handle_starttag(self, tag, attrs):
  if tag in ('script','style'): self.skip+=1
 def handle_endtag(self, tag):
  if tag in ('script','style'): self.skip=max(0,self.skip-1)
 def handle_data(self, data):
  if not self.skip and data.strip(): self.parts.append(data.strip())

def collect(item):
 key,url=item
 dest=ROOT/'sources'/key; dest.mkdir(parents=True,exist_ok=True)
 if (dest/'metadata.json').exists():
  return key,json.loads((dest/'metadata.json').read_text())['status']
 started=datetime.now(timezone.utc).isoformat()
 request=urllib.request.Request(url,headers={'User-Agent':'AgentResearch-Benchmark-Collection/1.0','Accept':'application/vnd.github+json' if 'api.github.com' in url else '*/*'})
 try:
  try: response=urllib.request.urlopen(request,timeout=35)
  except urllib.error.HTTPError as exc: response=exc
  with response:
   raw=response.read(); status=response.status; final_url=response.url
   headers={k:v for k,v in response.headers.items() if k.lower() in ('date','etag','last-modified','content-type','link','x-ratelimit-remaining')}
  (dest/'body').write_bytes(raw)
  text=raw.decode('utf-8',errors='replace')
  if '<html' in text[:2000].lower() or '<!doctype html' in text[:100].lower():
   parser=Text(); parser.feed(text); text='\n'.join(parser.parts)
  (dest/'text.txt').write_text(text,encoding='utf-8')
  metadata=dict(id=key,requested_url=url,final_url=final_url,status=status,retrieved_at=started,headers=headers,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
  (dest/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
  return key,status
 except Exception as exc:
  return key,str(exc)

if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
  for key,status in executor.map(collect,SOURCES.items()): print(key,status,flush=True)
