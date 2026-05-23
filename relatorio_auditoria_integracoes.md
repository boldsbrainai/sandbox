<!-- markdownlint-disable MD034 MD060 -->

# Relatório de Auditoria de Integrações

## Escopo e premissas

- O módulo chamado "Construção do Dossiê" não existe nominalmente neste repositório.
- Também não há ocorrência de "Dossiê", "Dossie" ou "Dossier" no código, nos nomes de arquivos ou na documentação.
- Para não interromper a auditoria, a análise foi executada sobre o código efetivamente presente no workspace, tratando como "documentação existente" os arquivos README, a documentação do site em [website/docs](website/docs) e os READMEs dos exemplos.
- O foco desta auditoria foi identificar chamadas externas reais ou simuladas, inclusive para serviços locais expostos via HTTP, WebSocket, MCP e SDKs.

## Contexto investigado

- Código de avaliação e agent loop em [evaluation](evaluation)
- SDK Python gerado e providers em [sdk/python/agent_sandbox](sdk/python/agent_sandbox)
- Exemplos de integração em [examples](examples)
- Documentação principal em [README.md](README.md) e [website/docs](website/docs)

## Fase 1: Mapeamento 360º de APIs e serviços externos

| Serviço / Provider | Endpoint completo e método HTTP | Arquivo / classe / função de origem | Tipo de autenticação identificada | Evidência e observações |
|---|---|---|---|---|
| OpenAI API | POST https://api.openai.com/v1/chat/completions | [examples/openai-integration/main.py](examples/openai-integration/main.py), classe OpenAI; [evaluation/agent_loop.py](evaluation/agent_loop.py), classe OpenAIAgentLoop | Chave de API via OPENAI_API_KEY | Chamada feita por client.chat.completions.create(). O endpoint aparece de forma implícita pelo SDK oficial OpenAI. |
| Azure OpenAI Service | POST https://{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION} | [evaluation/agent_loop.py](evaluation/agent_loop.py), classe AzureOpenAIAgentLoop | Chave de API via AZURE_OPENAI_API_KEY | O código instancia AzureOpenAI com azure_endpoint, api_key e api_version. O deployment é usado como model na chamada create(). |
| MiniMax OpenAI-Compatible API | POST https://api.minimax.io/v1/chat/completions | [examples/minimax-integration/main.py](examples/minimax-integration/main.py), função main; [evaluation/agent_loop.py](evaluation/agent_loop.py), classe OpenAIAgentLoop | Chave de API via MINIMAX_API_KEY | Integração OpenAI-compatible com base_url hardcoded no exemplo. Há regra específica de temperature > 0. |
| Volcengine VEFAAS API | POST encapsulado pelo SDK externo volcenginesdkvefaas para operações CreateSandbox, KillSandbox, DescribeSandbox, SetSandboxTimeout e ListSandboxes | [sdk/python/agent_sandbox/providers/volcengine.py](sdk/python/agent_sandbox/providers/volcengine.py), classe VolcengineProvider | Access key e secret key via VOLCENGINE_ACCESS_KEY e VOLCENGINE_SECRET_KEY | O repositório usa o SDK oficial da Volcengine e não expõe o URI REST final dessas operações no código local. |
| Volcengine Open API: ListTriggers | POST https://open.volcengineapi.com/?Action=ListTriggers&Version=2024-06-06 | [sdk/python/agent_sandbox/providers/volcengine.py](sdk/python/agent_sandbox/providers/volcengine.py), método _get_apig_trigger; [sdk/python/agent_sandbox/providers/sign.py](sdk/python/agent_sandbox/providers/sign.py), função request | Assinatura HMAC-SHA256 em header Authorization, com Host, X-Date, X-Content-Sha256 e opcional X-Security-Token | Chamada usada para descobrir trigger do tipo apig associado a uma function. |
| Volcengine Open API: ListRoutes | POST https://open.volcengineapi.com/?Action=ListRoutes&Version=2022-11-12 | [sdk/python/agent_sandbox/providers/volcengine.py](sdk/python/agent_sandbox/providers/volcengine.py), método _get_apig_domains; [sdk/python/agent_sandbox/providers/sign.py](sdk/python/agent_sandbox/providers/sign.py), função request | Assinatura HMAC-SHA256 em header Authorization, com Host, X-Date, X-Content-Sha256 e opcional X-Security-Token | Chamada usada para resolver domínios APIG públicos do sandbox. |
| Amazon Simple Storage Service ou endpoint compatível com S3 | PUT lógico via upload_fileobj para bucket S3; endpoint real é https://s3.{region}.amazonaws.com ou o valor de OSS_ENDPOINT quando configurado | [examples/oss-upload/aws-s3.py](examples/oss-upload/aws-s3.py), função _build_s3_client e main | Access key e secret key via AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY, com fallback OSS_ACCESS_KEY_ID / OSS_SECRET_ACCESS_KEY | Usa boto3 com assinatura s3v4. Suporta endpoint compatível com S3, incluindo provedores não AWS. |
| Volcano Engine TOS | PUT lógico para objeto no bucket via SDK tos.TosClientV2.put_object; endpoint real vem de TOS_ENDPOINT | [examples/oss-upload/main.py](examples/oss-upload/main.py), função main | Access key e secret key via TOS_ACCESS_KEY e TOS_SECRET_KEY | O método put_object recebe bucket, object_key e stream do arquivo vindo do sandbox. |
| AIO Sandbox MCP Hub | GET http://localhost:8080/mcp; POST http://localhost:8080/mcp para tools/call e list_tools no protocolo MCP streamable HTTP | [evaluation/main.py](evaluation/main.py), funções init_global_mcp_session e get_mcp_tools; [website/docs/en/guide/basic/mcp.md](website/docs/en/guide/basic/mcp.md) | Sem autenticação na configuração local padrão | Não é third-party, mas é um serviço externo ao processo que concentra Browser, File, Terminal e Markitdown. |
| AIO Sandbox Browser API: browser info | GET http://localhost:8080/v1/browser/info | [sdk/python/agent_sandbox/browser/raw_client.py](sdk/python/agent_sandbox/browser/raw_client.py), método get_info; consumido por [examples/playwright-integration/main.py](examples/playwright-integration/main.py) e exemplos browser-use | Sem autenticação na configuração local padrão | Retorna cdp_url usado por Playwright e browser-use. |
| AIO Sandbox Browser API: screenshot | GET http://localhost:8080/v1/browser/screenshot | [sdk/python/agent_sandbox/browser/raw_client.py](sdk/python/agent_sandbox/browser/raw_client.py), método screenshot; consumido por [examples/browser-use-cua/main.py](examples/browser-use-cua/main.py) | Sem autenticação na configuração local padrão | Streaming de bytes da captura de tela. |
| AIO Sandbox Browser API: execute action | POST http://localhost:8080/v1/browser/actions | [sdk/python/agent_sandbox/browser/raw_client.py](sdk/python/agent_sandbox/browser/raw_client.py), método execute_action; consumido por [examples/browser-use-cua/main.py](examples/browser-use-cua/main.py) | Sem autenticação na configuração local padrão | Usado como fallback CUA-style para click, drag, typing, press, scroll e wait. |
| AIO Sandbox Browser Page API: navigate | POST http://localhost:8080/v1/browser/page/navigate | [sdk/python/agent_sandbox/browser_page/raw_client.py](sdk/python/agent_sandbox/browser_page/raw_client.py), método navigate | Sem autenticação na configuração local padrão | Endpoint first-party/local, documentado como parte da API do sandbox. |
| AIO Sandbox Browser Page API: click | POST http://localhost:8080/v1/browser/page/click | [sdk/python/agent_sandbox/browser_page/raw_client.py](sdk/python/agent_sandbox/browser_page/raw_client.py), método click | Sem autenticação na configuração local padrão | Endpoint first-party/local, documentado como parte da API do sandbox. |
| AIO Sandbox Browser Page API: fill | POST http://localhost:8080/v1/browser/page/fill | [sdk/python/agent_sandbox/browser_page/raw_client.py](sdk/python/agent_sandbox/browser_page/raw_client.py), método fill | Sem autenticação na configuração local padrão | Endpoint first-party/local, documentado como parte da API do sandbox. |
| AIO Sandbox Bash API: exec | POST http://localhost:8080/v1/bash/exec | [sdk/python/agent_sandbox/bash/raw_client.py](sdk/python/agent_sandbox/bash/raw_client.py), método exec; consumido indiretamente por [examples/ag2-integration/main.py](examples/ag2-integration/main.py) e [examples/langgraph-deepagents-integration/main.py](examples/langgraph-deepagents-integration/main.py) | Sem autenticação na configuração local padrão | Serviço externo first-party/local, não third-party. |
| AIO Sandbox Bash API: output | POST http://localhost:8080/v1/bash/output | [sdk/python/agent_sandbox/bash/raw_client.py](sdk/python/agent_sandbox/bash/raw_client.py), método output | Sem autenticação na configuração local padrão | Streaming incremental por offsets. |
| AIO Sandbox Auth API: create ticket | POST http://localhost:8080/tickets | [sdk/python/agent_sandbox/auth/raw_client.py](sdk/python/agent_sandbox/auth/raw_client.py), método create_ticket | Sem autenticação para gerar ticket, segundo o contrato local | Endpoint local para emissão de ticket de curta duração. |
| AIO Sandbox Auth API: authenticate | GET http://localhost:8080/auth | [sdk/python/agent_sandbox/auth/raw_client.py](sdk/python/agent_sandbox/auth/raw_client.py), método authenticate | Ticket em x-original-uri ou JWT em Authorization | Serviço local de autenticação frontado por auth_request. |
| Chrome DevTools Protocol exposto pelo sandbox | WebSocket em cdp_url retornado por GET http://localhost:8080/v1/browser/info | [examples/playwright-integration/main.py](examples/playwright-integration/main.py), função main; [examples/browser-use-integration/main.py](examples/browser-use-integration/main.py) | Sem autenticação explícita no código do exemplo | O endpoint exato do WebSocket é dinâmico e retornado pela API local. |
| Playwright para navegação em site real | Navegação HTTP para https://duckduckgo.com e demais URLs informadas pelo script | [examples/playwright-integration/main.py](examples/playwright-integration/main.py), função main | Sem autenticação para o alvo visitado no exemplo | A chamada externa efetiva é feita pelo navegador controlado via CDP. |
| browser-use com modelo compatível OpenAI | Chamadas de modelo encapsuladas por browser_use.llm.ChatOpenAI; endpoint depende da configuração da biblioteca e do ambiente | [examples/browser-use-integration/main.py](examples/browser-use-integration/main.py), função main; [examples/browser-use-cua/main.py](examples/browser-use-cua/main.py) | Chave de API do provider do modelo, normalmente OPENAI_API_KEY ou equivalente | O código não fixa base_url; ele fixa o model e delega o transporte à biblioteca browser-use. |
| browser-use para navegação em site real | Navegação HTTP para https://duckduckgo.com e demais URLs do task | [examples/browser-use-integration/main.py](examples/browser-use-integration/main.py), classe Agent; [examples/browser-use-cua/main.py](examples/browser-use-cua/main.py) | Sem autenticação para o alvo visitado no exemplo | A saída real depende do browser_session conectado ao sandbox. |
| AG2 via provider OpenAI | POST para endpoint compatível com OpenAI definido internamente pela biblioteca autogen, usando model e api_type openai | [examples/ag2-integration/main.py](examples/ag2-integration/main.py), função main, classe LLMConfig | OPENAI_API_KEY | O código declara explicitamente api_type=openai, mas não fixa base_url. |
| LangGraph / DeepAgents via provider OpenAI-compatible | POST para base_url definido em OPENAI_BASEURL, com rota compatível com OpenAI da biblioteca langchain | [examples/langgraph-deepagents-integration/main.py](examples/langgraph-deepagents-integration/main.py), função main, init_chat_model | OPENAI_API_KEY | O código permite OpenRouter ou outro provider compatível via OPENAI_BASEURL. |

## Fase 2: Matriz de Convergência

### Quadrante 1: Convergente (real e documentado)

1. OpenAI API
   - Está implementada em [examples/openai-integration/main.py](examples/openai-integration/main.py) e [evaluation/agent_loop.py](evaluation/agent_loop.py).
   - Está documentada no [README.md](README.md) e nos exemplos do repositório.
   - Risco arquitetural: baixo.

2. Azure OpenAI Service
   - Está implementada em [evaluation/agent_loop.py](evaluation/agent_loop.py).
   - Está ao menos prevista na documentação de alto nível do repositório e no próprio diretório [evaluation](evaluation).
   - Risco arquitetural: médio, porque a documentação operacional é mais rasa do que a implementação.

3. MiniMax OpenAI-Compatible API
   - Está implementada em [examples/minimax-integration/main.py](examples/minimax-integration/main.py) e no agent loop genérico.
   - Está documentada no [README.md](README.md).
   - Risco arquitetural: médio, porque existe regra especial de temperature e isso pode ser perdido em futuras refatorações.

4. VolcengineProvider para gestão de sandboxes
   - Está implementado em [sdk/python/agent_sandbox/providers/volcengine.py](sdk/python/agent_sandbox/providers/volcengine.py).
   - Está documentado em [sdk/python/agent_sandbox/providers/README.md](sdk/python/agent_sandbox/providers/README.md) e em [examples/volcengine-provider/main.py](examples/volcengine-provider/main.py).
   - Risco arquitetural: médio, porque parte do fluxo depende de descoberta indireta de domínio APIG.

5. AIO Sandbox MCP Hub e APIs HTTP locais
   - Estão implementados no SDK e consumidos extensivamente pelos exemplos e pelo motor de avaliação.
   - Estão documentados no [README.md](README.md) e em [website/docs/en/guide/basic/mcp.md](website/docs/en/guide/basic/mcp.md).
   - Embora não sejam third-party, são integrações externas reais ao processo.
   - Risco arquitetural: baixo.

6. Playwright via CDP do sandbox
   - Está implementado em [examples/playwright-integration/main.py](examples/playwright-integration/main.py).
   - Está documentado em [examples/playwright-integration/README.md](examples/playwright-integration/README.md) e no [README.md](README.md).
   - Risco arquitetural: baixo.

7. AG2 e LangGraph / DeepAgents
   - Estão implementados em [examples/ag2-integration/main.py](examples/ag2-integration/main.py) e [examples/langgraph-deepagents-integration/main.py](examples/langgraph-deepagents-integration/main.py).
   - Estão documentados nos respectivos READMEs dos exemplos.
   - Risco arquitetural: médio, porque delegam a resolução final do endpoint do LLM para bibliotecas externas ou variáveis de ambiente.

### Quadrante 2: Divergente por omissão (Shadow API)

1. Volcengine Open API para ListTriggers e ListRoutes
   - As chamadas para https://open.volcengineapi.com com ações ListTriggers e ListRoutes existem no código em [sdk/python/agent_sandbox/providers/volcengine.py](sdk/python/agent_sandbox/providers/volcengine.py) e [sdk/python/agent_sandbox/providers/sign.py](sdk/python/agent_sandbox/providers/sign.py).
   - A documentação local menciona o provider Volcengine, mas não explicita esse subfluxo de descoberta APIG.
   - Risco crítico: existe dependência arquitetural oculta de APIG para resolver domínios públicos do sandbox. Em auditoria de produção isso costuma aparecer como integração invisível, difícil de governar e fácil de quebrar em mudanças de plataforma.

2. Upload para Amazon Simple Storage Service ou endpoint compatível com S3
   - Existe implementação real em [examples/oss-upload/aws-s3.py](examples/oss-upload/aws-s3.py).
   - O README do diretório [examples/oss-upload/README.md](examples/oss-upload/README.md) não descreve a integração com S3 nem os requisitos de credencial e endpoint compatível.
   - Risco crítico: integração cloud real presente no código, mas não coberta pela documentação do exemplo correspondente.

3. Upload para Volcano Engine TOS
   - Existe implementação real em [examples/oss-upload/main.py](examples/oss-upload/main.py).
   - O README do diretório [examples/oss-upload/README.md](examples/oss-upload/README.md) continua descrevendo operações básicas de arquivo, não TOS.
   - Risco crítico: falsa percepção de escopo do módulo. Quem lê a documentação acredita que é apenas file upload interno no sandbox, quando há saída para armazenamento externo.

4. Serviço local de autenticação por ticket e JWT
   - O contrato existe no SDK em [sdk/python/agent_sandbox/auth/raw_client.py](sdk/python/agent_sandbox/auth/raw_client.py).
   - A documentação principal não destaca esse fluxo; a evidência mais clara aparece espalhada em exemplos e blog.
   - Risco arquitetural: médio. É uma superfície de autenticação relevante que está subexposta na documentação principal.

### Quadrante 3: Hardcoded / Stubs / Mocks

1. Mocks de OpenAI e Azure OpenAI nos testes
   - [evaluation/tests/test_openai_agent_loop.py](evaluation/tests/test_openai_agent_loop.py) usa patch, MagicMock e AsyncMock para simular a API.
   - Isso é correto para testes unitários, mas precisa ser separado explicitamente da narrativa de produção.
   - Risco arquitetural: baixo no teste, alto se alguém inferir cobertura de integração real a partir desses testes.

2. Placeholders de credencial e endpoint no fluxo de avaliação
   - [evaluation/main.py](evaluation/main.py) usa valores default como https://your-endpoint.openai.azure.com e your-api-key.
   - [evaluation/.env.example](evaluation/.env.example) replica os placeholders.
   - Risco arquitetural: médio. Se a pipeline não validar configuração obrigatória, a aplicação pode parecer configurada, mas na prática rodar contra valores de exemplo.

3. Hardcode recorrente de http://localhost:8080
   - Aparece em [README.md](README.md), exemplos, SDK e docs.
   - Não é um mock por si só, mas é um endpoint hardcoded de ambiente local, não um endpoint de produção.
   - Risco arquitetural: médio. Promove forte acoplamento ao modo local e exige disciplina operacional para ambientes remotos.

4. URLs demonstrativas como https://example.com e https://duckduckgo.com
   - Aparecem em exemplos e documentação.
   - São exemplos, não integrações corporativas de produção.
   - Risco arquitetural: baixo, desde que não sejam confundidas com fluxos homologados.

## Riscos arquiteturais críticos

1. Shadow APIs de descoberta na Volcengine
   - O provider não depende apenas do SDK principal de sandbox. Ele também faz chamadas manuais para open.volcengineapi.com para descobrir triggers e rotas.
   - Isso cria acoplamento implícito com APIG, difícil de rastrear por quem lê apenas o README do provider.

2. Divergência documental no exemplo de upload
   - O diretório [examples/oss-upload](examples/oss-upload) contém integrações reais com armazenamento externo, mas o README descreve apenas operações básicas de arquivo.
   - Isso é o achado mais forte de convergência ruim entre código e documentação neste repositório.

3. Placeholders operacionais em runtime de avaliação
   - O motor de avaliação aceita defaults de exemplo para Azure OpenAI.
   - Sem uma validação explícita de configuração obrigatória, existe risco de execução enganosa, troubleshooting ruidoso e falhas silenciosas.

4. Superfície de autenticação pouco destacada
   - Os endpoints locais POST /tickets e GET /auth existem e são relevantes, mas não aparecem com a mesma evidência da API principal e do MCP Hub.
   - Em auditoria de segurança, isso costuma virar ponto cego de governança.

## Conclusão executiva

- O artefato solicitado como "Construção do Dossiê" não está neste workspace.
- Mesmo assim, a investigação revelou um conjunto claro de integrações externas reais.
- As integrações mais bem convergentes são OpenAI, MiniMax, MCP Hub, Playwright, AG2 e LangGraph.
- Os principais desvios estão em duas áreas: shadow APIs da Volcengine usadas para descoberta de APIG e o diretório [examples/oss-upload](examples/oss-upload), cujo código fala com storage externo, mas cuja documentação não acompanha esse comportamento.
- O principal grupo de stubs e mocks está corretamente restrito ao teste unitário em [evaluation/tests/test_openai_agent_loop.py](evaluation/tests/test_openai_agent_loop.py).

## Recomendação objetiva

1. Renomear ou corrigir o README de [examples/oss-upload](examples/oss-upload) para refletir explicitamente Amazon Simple Storage Service, TOS e endpoints compatíveis com S3.
2. Documentar no provider da Volcengine o fluxo indireto de ListTriggers e ListRoutes, incluindo dependência de APIG.
3. Tornar obrigatória a validação de variáveis de ambiente críticas no fluxo de avaliação para impedir execução com placeholders.
4. Promover os endpoints de autenticação local para a documentação principal de arquitetura e operação.

<!-- markdownlint-enable MD034 MD060 -->