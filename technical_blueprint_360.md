<!-- markdownlint-disable MD060 -->

# Technical Blueprint 360º

## Visão Executiva

O repositório implementa um produto centrado em um ambiente de sandbox unificado para agentes de inteligência artificial, distribuído principalmente como imagem de container e exposto por uma API HTTP e um hub MCP. O código-fonte presente no workspace não contém o backend operacional completo do serviço; em vez disso, concentra:

- documentação e portal de API;
- SDK Python gerado;
- SDK JavaScript e TypeScript;
- exemplos de integração com provedores de modelo e automação;
- framework de avaliação de agentes e tools.

Em termos arquiteturais, o repositório é melhor descrito como um monorepo de produto e SDKs para uma plataforma de sandbox agent-ready, com elementos fortes de sistema multiagente na camada de exemplos e avaliação.

## Fase 1: Topografia de Stack e Infraestrutura

### Core Stack

| Camada | Stack identificada | Evidência |
|---|---|---|
| Backend exposto | FastAPI, com OpenAPI 3.1.0 | [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json) declara title FastAPI; a superfície de rotas está toda no spec |
| Runtime HTTP do backend | Uvicorn como servidor ou relay de partes do serviço | [website/docs/en/blog/announcing-0.mdx](website/docs/en/blog/announcing-0.mdx) descreve relay de CDP via uvicorn; o backend não está implementado no repo, mas a docs o assume |
| SDK backend-facing em Python | Python 3.8+ com httpx, pydantic, Fern-generated client | [sdk/python/pyproject.toml](sdk/python/pyproject.toml), [sdk/python/agent_sandbox/client.py](sdk/python/agent_sandbox/client.py) |
| SDK backend-facing em JavaScript e TypeScript | TypeScript, compilação para CommonJS e ESM | [sdk/js/package.json](sdk/js/package.json) |
| Portal web / documentação | React via Rspress, Rsbuild e tema customizado | [website/package.json](website/package.json), [website/rspress.config.ts](website/rspress.config.ts), [website/theme/index.tsx](website/theme/index.tsx) |
| Framework de avaliação | Python com OpenAI SDK e MCP SDK | [evaluation/pyproject.toml](evaluation/pyproject.toml), [evaluation/agent_loop.py](evaluation/agent_loop.py), [evaluation/main.py](evaluation/main.py) |
| Integrações de agentes | OpenAI SDK, Azure OpenAI SDK, AG2, browser-use, Playwright, LangGraph DeepAgents | [examples](examples), [evaluation/agent_loop.py](evaluation/agent_loop.py) |

### Infraestrutura e Containerização

| Item | Leitura forense | Evidência |
|---|---|---|
| Modelo de deploy principal | Container único all-in-one | [README.md](README.md), [docker-compose.yaml](docker-compose.yaml) |
| Estratégia de execução local | docker run direto ou docker-compose com um serviço sandbox | [README.md](README.md), [docker-compose.yaml](docker-compose.yaml) |
| Composição do container | Browser, VNC, MCP Hub, VSCode Server, Jupyter, shell, proxy e serviços auxiliares | [README.md](README.md), variáveis de ambiente em [docker-compose.yaml](docker-compose.yaml) |
| Recursos provisionados | shm de 2 GB, limite de memória de 8 GB, 4 CPUs, múltiplas portas internas | [docker-compose.yaml](docker-compose.yaml) |
| Estratégia de imagem | espelhamento de imagem publicada na Volcengine para GHCR | [\.github/workflows/push-to-ghcr.yml](.github/workflows/push-to-ghcr.yml) |
| Deploy de docs | build estático Rspress e preview local; não há pipeline dedicada de publicação do site neste repo | [website/package.json](website/package.json) |

### CI/CD

| Workflow | Responsabilidade | Evidência |
|---|---|---|
| [\.github/workflows/push-to-ghcr.yml](.github/workflows/push-to-ghcr.yml) | Espelha imagem multi-arquitetura para GitHub Container Registry em release ou dispatch | workflow de mirror a partir de enterprise-public-cn-beijing.cr.volces.com |
| [\.github/workflows/sdk-ci.yml](.github/workflows/sdk-ci.yml) | Build e testes do SDK JavaScript | Node 20, pnpm 9, build com rslib e testes com vitest |
| [\.github/workflows/sdk-publish.yml](.github/workflows/sdk-publish.yml) | Publicação versionada dos SDKs JavaScript e Python | npm publish, twine upload, bump de versão e commit automatizado |

### Gerenciamento de Pacotes, Build, Lint e Formatação

| Ecossistema | Ferramentas | Evidência |
|---|---|---|
| Workspace JavaScript | pnpm workspace | [pnpm-workspace.yaml](pnpm-workspace.yaml) |
| Site | npm scripts via package.json, mas resolvido no monorepo com pnpm | [website/package.json](website/package.json), [pnpm-workspace.yaml](pnpm-workspace.yaml) |
| SDK JavaScript | rslib, TypeScript, vitest, rimraf | [sdk/js/package.json](sdk/js/package.json) |
| SDK Python | setuptools e wheel | [sdk/python/pyproject.toml](sdk/python/pyproject.toml) |
| Avaliação e exemplos Python | uv | [evaluation/pyproject.toml](evaluation/pyproject.toml) e presença consistente de uv.lock nos exemplos |
| Lint e formatting JS e docs | Biome e Prettier | [package.json](package.json), [biome.json](biome.json), [website/package.json](website/package.json) |

## Fase 2: Padrões Arquiteturais e Topologia

### Padrão Global

- O repositório não é um backend monolítico clássico com código da API inteira em source; ele é um monorepo de distribuição e integração de uma plataforma de sandbox.
- O produto em runtime é um monolito operacional dentro de um único container, com múltiplos subsistemas acoplados por filesystem e rede interna.
- Há elementos claros de sistema multiagente na camada de consumo:
  - AG2 multi-agent em [examples/ag2-integration/main.py](examples/ag2-integration/main.py);
  - browser-use agent em [examples/browser-use-integration/main.py](examples/browser-use-integration/main.py);
  - DeepAgents e LangGraph em [examples/langgraph-deepagents-integration/main.py](examples/langgraph-deepagents-integration/main.py);
  - evaluation loop com tool calling em [evaluation/agent_loop.py](evaluation/agent_loop.py).
- A melhor classificação arquitetural é: monorepo de produto + SDKs para um monólito operacional containerizado, com forte orientação a ferramentas, MCP e workloads agentic.

### Mapeamento de Diretórios e Domain Boundaries

| Diretório | Responsabilidade arquitetural | Evidência |
|---|---|---|
| [sdk/python](sdk/python) | SDK Python gerado para consumir a API do sandbox e providers cloud | [sdk/python/agent_sandbox/client.py](sdk/python/agent_sandbox/client.py) expõe módulos sandbox, file, bash, browser, jupyter, nodejs, proxy, auth, mcp |
| [sdk/js](sdk/js) | SDK JavaScript e TypeScript com build, testes e exemplos | [sdk/js/package.json](sdk/js/package.json), [sdk/js/README.md](sdk/js/README.md) |
| [sdk/fern](sdk/fern) | Configuração de geração de SDKs por Fern | presença da pasta e arquivos de geração no tree fornecido |
| [website](website) | Portal de documentação, homepage do produto e API reference | [website/rspress.config.ts](website/rspress.config.ts), [website/docs/en/api/index.tsx](website/docs/en/api/index.tsx) |
| [website/docs/public/v1](website/docs/public/v1) | Contrato OpenAPI versionado usado como fonte de verdade da superfície de API | [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json) |
| [examples](examples) | Blueprints de consumo da plataforma com LLMs, automação, storage e frameworks agentic | múltiplos subdiretórios por integração |
| [evaluation](evaluation) | Harness de avaliação automatizada de tasks MCP com diferentes providers de modelo | [evaluation/main.py](evaluation/main.py), [evaluation/agent_loop.py](evaluation/agent_loop.py) |
| [public](public) | Arquivos estáticos raiz do portal | árvore de diretórios do workspace |
| [theme](theme) | Tema customizado adicional do site | árvore de diretórios do workspace |
| [docker](docker) | Não contém código relevante no estado atual | só contém .gitkeep |

### Fluxo de Controle

#### Fluxo típico de cliente para o sandbox

1. Um cliente consome o SDK Python ou JavaScript.
2. O SDK serializa a chamada HTTP para o endpoint documentado no OpenAPI.
3. O serviço FastAPI no container recebe a requisição.
4. O runtime interno despacha para um dos subsistemas locais:
   - shell e bash;
   - file;
   - Jupyter;
   - Node.js REPL;
   - browser e CDP relay;
   - proxy;
   - auth;
   - MCP hub.
5. O resultado retorna em formato padronizado Response e derivados, preservando compatibilidade com respostas antigas em alguns casos, como browser actions.

#### Fluxo típico agentic via MCP

1. O agente conecta em [evaluation/main.py](evaluation/main.py) ao endpoint MCP streamable HTTP em /mcp.
2. O MCP Hub lista tools agregadas de browser, file, shell e markitdown.
3. O loop do agente em [evaluation/agent_loop.py](evaluation/agent_loop.py) chama o provider de modelo.
4. O provider retorna tool_calls.
5. O loop invoca mcp_session.call_tool e injeta o resultado de volta na conversa.
6. O modelo produz a resposta final.

#### Fluxo até banco de dados

- Não há evidência de banco de dados operacional, ORM ou camada persistente tradicional neste repositório.
- O fluxo dominante é client → API do container → subsistema em memória, filesystem do sandbox ou serviço de processo local.
- Onde existe retenção de estado, ela ocorre em:
  - sessões de bash;
  - sessões de Jupyter;
  - sessões de Node.js;
  - estado do browser, cookies e tabs;
  - arquivos persistidos no filesystem do sandbox.

## Fase 3: Modelagem de Dados e Persistência

### ORM / Query Builders

- Não há evidência de Prisma, Drizzle, SQLAlchemy, TypeORM, Sequelize, Mongoose ou query builder SQL no código-fonte e manifests analisados.
- O modelo de dados é API-first, tipado por OpenAPI e refletido em classes geradas por Fern nos SDKs.

### Schemas e Entidades Principais

As entidades centrais aparecem como modelos da API em [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json) e tipos gerados no SDK Python.

| Entidade / conceito | Papel | Evidência |
|---|---|---|
| SandboxResponse | Contexto do sandbox, diretórios, versão e ambiente | rota /v1/sandbox em [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json) |
| BashSessionInfo | Sessão persistente de bash | rotas /v1/bash/sessions em [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json) |
| Jupyter session | Sessão de notebook com kernel e outputs | rotas /v1/jupyter/sessions em [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json) |
| NodeJs session | Sessão de REPL Node.js | rotas /v1/nodejs/sessions em [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json) |
| FileInfo e derivados | Metadados de arquivo e operações de filesystem | rotas /v1/file/* no OpenAPI |
| Browser action and browser state models | Ações de GUI, viewport, tabs, cookies e storage | rotas /v1/browser/* no OpenAPI e clientes em [sdk/python/agent_sandbox/browser](sdk/python/agent_sandbox/browser) |
| RouteResponseModel | Modelo de interceptação e mocking de rede do browser | [sdk/python/agent_sandbox/types/route_response_model.py](sdk/python/agent_sandbox/types/route_response_model.py), rotas /v1/browser/network/route |
| Hook e reports de observação | Lifecycle hooks e relatórios de observabilidade do sandbox | rotas /v1/sandbox/hooks e /v1/sandbox/observe/* |
| Auth ticket | Credencial efêmera para acesso autenticado | rotas /tickets e /auth |

### Persistência

- Persistência principal: filesystem do container sandbox.
- Persistência de sessão: mantida por subsistemas locais do processo para bash, Jupyter, Node.js e browser.
- Export e artefatos: arquivos, HAR de rede, screenshots, markdown convertido, relatórios de observação.
- Persistência externa opcional nos exemplos:
  - Amazon Simple Storage Service ou endpoints compatíveis com S3 em [examples/oss-upload/aws-s3.py](examples/oss-upload/aws-s3.py);
  - Volcano Engine TOS em [examples/oss-upload/main.py](examples/oss-upload/main.py).

### Gerenciamento de Estado

#### Backend

- Estado transitório e operacional, não relacional.
- Gerenciado por sessões e recursos do sandbox:
  - processos shell;
  - kernels Jupyter;
  - runtime Node.js;
  - tabs, cookies e browser state;
  - watchers de arquivo;
  - observação do sandbox.

#### Frontend

- Não há evidência de Redux, Zustand, MobX, Recoil, Jotai ou store global dedicada.
- O site é essencialmente estático, com estado de interface simples provido por React e runtime do Rspress, como useDark, useI18n e usePageData em [website/theme/index.tsx](website/theme/index.tsx) e [website/theme/components/HomeLayout.tsx](website/theme/components/HomeLayout.tsx).

## Fase 4: Hub de Integrações e Superfície de API

### APIs e Gateways expostos

Os grupos de rotas centrais estão descritos em [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json).

| Grupo | Rotas principais | Evidência |
|---|---|---|
| Sandbox | /v1/sandbox, /v1/sandbox/packages/python, /v1/sandbox/packages/nodejs, /v1/sandbox/hooks, /v1/sandbox/observe/* | OpenAPI |
| Bash | /v1/bash/exec, /v1/bash/output, /v1/bash/write, /v1/bash/kill, /v1/bash/sessions* | OpenAPI |
| File | /v1/file/read, write, replace, search, find, grep, glob, upload, download, list, watch* | OpenAPI |
| Jupyter | /v1/jupyter/execute, info, sessions, sessions/create | OpenAPI |
| Node.js | /v1/nodejs/execute, info, sessions* | OpenAPI |
| MCP | /v1/mcp/servers, /v1/mcp/{server_name}/tools, /v1/mcp/{server_name}/tools/{tool_name}, além de /mcp e /v1/mcp no runtime | [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json), [website/docs/en/guide/basic/mcp.md](website/docs/en/guide/basic/mcp.md) |
| Browser | /v1/browser/info, screenshot, actions, config, restart, proxy.pac | OpenAPI |
| Browser Page | /v1/browser/page/navigate, click, fill, type, hot_key, hover, upload_file, fill_form, screenshot, html, text, markdown, evaluate, wait e outras | OpenAPI |
| Browser Tabs, Cookies, State e Network | /v1/browser/tabs*, /v1/browser/cookies, /v1/browser/state/*, /v1/browser/network/* | OpenAPI |
| Proxy | /v1/proxy/mappings, excludes, diagnose, health, upstream | OpenAPI |
| Auth | /tickets, /auth | OpenAPI |
| Utilitário de conversão | endpoint de conversão de URI para markdown | descrição e clientes em [sdk/python/agent_sandbox/util/client.py](sdk/python/agent_sandbox/util/client.py) e OpenAPI |

### Third-Party APIs e integrações externas

| Integração | Papel | Evidência |
|---|---|---|
| OpenAI API | Provider padrão de modelo nos exemplos e no evaluation loop | [examples/openai-integration/main.py](examples/openai-integration/main.py), [evaluation/agent_loop.py](evaluation/agent_loop.py) |
| Azure OpenAI Service | Provider enterprise no loop de avaliação | [evaluation/agent_loop.py](evaluation/agent_loop.py) |
| MiniMax API | Provider OpenAI-compatible | [examples/minimax-integration/main.py](examples/minimax-integration/main.py) |
| OpenRouter ou qualquer provider OpenAI-compatible | Backend de modelo em DeepAgents example | [examples/langgraph-deepagents-integration/main.py](examples/langgraph-deepagents-integration/main.py), [examples/langgraph-deepagents-integration/README.md](examples/langgraph-deepagents-integration/README.md) |
| Volcengine VEFAAS | Provisionamento e lifecycle de sandboxes cloud | [sdk/python/agent_sandbox/providers/volcengine.py](sdk/python/agent_sandbox/providers/volcengine.py), [sdk/js/README.md](sdk/js/README.md) |
| Volcengine Open API e APIG | Descoberta de rotas e domínios via assinatura HMAC-SHA256 | [sdk/python/agent_sandbox/providers/sign.py](sdk/python/agent_sandbox/providers/sign.py) |
| Volcano Engine TOS | Upload de artefatos externos | [examples/oss-upload/main.py](examples/oss-upload/main.py) |
| Amazon S3 ou endpoint compatível | Upload de artefatos externos | [examples/oss-upload/aws-s3.py](examples/oss-upload/aws-s3.py) |
| Playwright | Automação browser sobre CDP | [examples/playwright-integration/main.py](examples/playwright-integration/main.py) |
| browser-use | Agent browser-driven | [examples/browser-use-integration/main.py](examples/browser-use-integration/main.py), [examples/browser-use-cua/main.py](examples/browser-use-cua/main.py) |
| AG2 / AutoGen | Orquestração multiagente | [examples/ag2-integration/main.py](examples/ag2-integration/main.py) |
| LangGraph DeepAgents | Framework de agente profundo | [examples/langgraph-deepagents-integration/main.py](examples/langgraph-deepagents-integration/main.py) |

Não há evidência de gateways de pagamento, APIs meteorológicas, blockchain, telemetria de produto externa, mensageria empresarial ou banco gerenciado neste repositório.

### Autenticação e Autorização

| Mecanismo | Como aparece | Evidência |
|---|---|---|
| Ticket efêmero | POST /tickets cria ticket de curta duração | [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json), [sdk/python/agent_sandbox/auth/raw_client.py](sdk/python/agent_sandbox/auth/raw_client.py) |
| JWT | GET /auth valida JWT no header Authorization | [website/docs/public/v1/openapi.json](website/docs/public/v1/openapi.json), [sdk/python/agent_sandbox/auth/raw_client.py](sdk/python/agent_sandbox/auth/raw_client.py) |
| Integração com Nginx auth_request | endpoint /auth é descrito como backend de subrequest | OpenAPI |
| Configuração de chave pública JWT | variável JWT_PUBLIC_KEY no compose | [docker-compose.yaml](docker-compose.yaml) |
| Autorização de cloud providers | Access key, secret key e HMAC-SHA256 para Volcengine; access key e secret key para S3 e TOS | [sdk/python/agent_sandbox/providers/sign.py](sdk/python/agent_sandbox/providers/sign.py), exemplos de upload |

Não há evidência de RBAC detalhado, ACL por usuário, OAuth2 authorization code ou identity provider corporativo nesta base.

## Fase 5: UI/UX e Design System Engine

### Bibliotecas de Componentes e Estilização

| Item | Situação | Evidência |
|---|---|---|
| React | Sim, via Rspress | [website/package.json](website/package.json), [website/theme/index.tsx](website/theme/index.tsx) |
| Rspress Theme | Tema default estendido com componentes próprios | [website/theme/index.tsx](website/theme/index.tsx) |
| CSS / SCSS | SCSS customizado para landing page | [website/theme/components/HomeLayout.scss](website/theme/components/HomeLayout.scss) |
| Scalar API Reference | Render da documentação interativa da API | [website/docs/en/api/index.tsx](website/docs/en/api/index.tsx) |
| Tailwind CSS | Não identificado | ausência nos manifests |
| Radix UI | Não identificado | ausência nos manifests |
| shadcn/ui | Não identificado | ausência nos manifests |
| Material UI, Chakra ou Ant Design | Não identificados | ausência nos manifests |

### Filosofia de Design

- A interface não é um produto transacional de alta densidade; é uma landing page técnica e um portal documental para developer experience.
- A homepage adota uma linguagem visual de tooling platform:
  - grid com hero de código;
  - badges de capabilities;
  - ênfase em sandbox running e MCP Server active.
- Há dualidade light and dark mode baseada em variáveis CSS, não dark-first puro, com esquema visual deliberado para ambos os temas em [website/theme/components/HomeLayout.scss](website/theme/components/HomeLayout.scss).
- O tom visual prioriza:
  - confiabilidade de infraestrutura;
  - produto para agentes e desenvolvedores;
  - demonstração de capacidades por código e exemplos.
- A página de API desliga explicitamente telemetria na UI do Scalar em [website/docs/en/api/index.tsx](website/docs/en/api/index.tsx).

## Conclusões Arquiteturais Diretas

### O que o repositório é

- Um monorepo de distribuição de uma plataforma de sandbox agent-ready.
- Um hub de SDKs e documentação para uma API FastAPI executada em container único.
- Um laboratório de exemplos agentic e de avaliação de tools MCP.

### O que o repositório não é

- Não é um SaaS full-stack clássico com backend de negócio, frontend de produto e banco relacional visível.
- Não é uma malha de microserviços desacoplados por mensagens.
- Não expõe implementação completa do backend do container neste workspace.

## Avaliação de Débito Técnico / Riscos Arquiteturais

### 1. Backend operacional fora do repositório analisado

- O contrato de API está no repo, mas a implementação principal do serviço roda como imagem externa.
- Isso cria risco de drift entre OpenAPI, SDKs, documentação e comportamento real do container publicado.

### 2. Forte acoplamento ao container único

- Browser, shell, Jupyter, Node.js, proxy, VSCode e MCP compartilham o mesmo runtime e filesystem.
- Isso simplifica DX, mas aumenta blast radius operacional e complexidade de observabilidade quando há falhas cruzadas.

### 3. Estado operacional distribuído em múltiplos subsistemas locais

- Sessões de bash, Jupyter, Node.js, browser state e watchers coexistem dentro do mesmo ambiente.
- Sem uma camada explícita de persistência e coordenação externa, recuperação e debugging podem depender de artefatos transitórios.

### 4. Segurança baseada em borda simples

- Há ticket e JWT, mas não aparecem evidências de RBAC granular, multi-tenant isolation policy configurável ou trilha robusta de autorização por recurso neste repositório.
- Para um produto com execução de código e browser remotos, isso é uma superfície de risco relevante.

### 5. Shadow dependency de infraestrutura cloud

- O provider Volcengine depende de descoberta via Open API e APIG, não apenas do SDK principal, o que aumenta acoplamento com detalhes da plataforma cloud.
- Essa dependência é técnica e real, mas pouco visível na narrativa principal do produto.

### 6. Divergência entre alguns READMEs de exemplos e o comportamento real

- O exemplo de upload em [examples/oss-upload](examples/oss-upload) contém integrações reais com TOS e S3-compatible storage, mas a documentação local desse diretório não reflete esse escopo com precisão.

### 7. Geração de SDK como fonte derivada

- Os SDKs são fortemente derivados do contrato OpenAPI.
- Se o contrato mudar sem sincronização forte com a imagem runtime, a experiência do cliente degrada rapidamente.

### 8. Ausência de camada explícita de persistência pode mascarar limites de produto

- Para o caso de uso atual isso é coerente, mas limita workflows que exigem histórico forte, auditoria persistente ou colaboração multiusuário sem componentes adicionais.

## Síntese final

O blueprint real do repositório é o de uma plataforma de sandbox unificada para agentes de inteligência artificial, servida como container único e consumida por SDKs, docs e exemplos. O centro da arquitetura não é banco de dados nem UI de negócio; é a orquestração segura de capacidades de execução, browser, filesystem e MCP em um ambiente consolidado, com integração a providers de modelo e clouds específicas.

<!-- markdownlint-enable MD060 -->