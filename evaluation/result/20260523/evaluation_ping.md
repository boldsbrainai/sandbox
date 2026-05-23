
# Evaluation Report

## Summary

- **Scoring Mode**: tool-calling
- **Accuracy**: 0/1 (0.0%)
- **Average Task Duration**: 0.22s
- **Average Tool Calls per Task**: 0.00
- **Total Tool Calls**: 0

---

### Task 1

- **Prompt**: answer the aio system's version. like v1.0.0.1xx
- **Success Criterion**: `v1\.0\.0\.152`
- **Actual Response**: `TASK_EXECUTION_ERROR: NotFoundError: Error code: 404 - {'error': {'message': "model 'qwen3:latest' not found", 'type': 'not_found_error', 'param': None, 'code': None}}`
- **Correct**: ❌
- **Duration**: 0.22s
- **Tool Calls Summary**: No tools called



#### Summary
Task execution failed with NotFoundError

#### Feedback
Error during task execution: Error code: 404 - {'error': {'message': "model 'qwen3:latest' not found", 'type': 'not_found_error', 'param': None, 'code': None}}

---

## 📊 Detailed Summary Table

| # | Prompt | 操作时间 | 是否成功 | 工具调用数量 | 操作步骤 | 失败原因 |
|---|--------|----------|----------|--------------|----------|----------|
| 1 | answer the aio system's version. like v1.0.0.1xx | 0.22s | ❌ | 0 | N/A | TASK_EXECUTION_ERROR: NotFoundError: Error code: 404 - {'error': {'message': "model 'qwen3:latest' n |
