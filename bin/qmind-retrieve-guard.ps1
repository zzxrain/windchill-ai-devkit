$rawInput = [Console]::In.ReadToEnd()

try {
    $eventData = $rawInput | ConvertFrom-Json
}
catch {
    # If the hook payload itself cannot be parsed, do not interfere with
    # unrelated Qoder tool execution.
    exit 0
}

$toolName = ""
$mcpServerName = ""
$mcpToolName = ""
$originalRequestName = ""

if ($null -ne $eventData.tool_name) {
    $toolName = [string]$eventData.tool_name
}

if ($null -ne $eventData.original_request_name) {
    $originalRequestName = [string]$eventData.original_request_name
}

if ($null -ne $eventData.mcp_context) {
    if ($null -ne $eventData.mcp_context.server_name) {
        $mcpServerName = [string]$eventData.mcp_context.server_name
    }

    if ($null -ne $eventData.mcp_context.tool_name) {
        $mcpToolName = [string]$eventData.mcp_context.tool_name
    }
}

$isQMind =
    ($toolName -match "qoder-qmind") -or
    ($mcpServerName -match "qoder-qmind")

$isRetrieve =
    ($toolName -match "retrieve") -or
    ($mcpToolName -match "^retrieve$") -or
    ($originalRequestName -match "retrieve")

if (-not ($isQMind -and $isRetrieve)) {
    exit 0
}

$notebookId = ""
$query = ""

if ($null -ne $eventData.tool_input) {
    if ($null -ne $eventData.tool_input.notebookId) {
        $notebookId = [string]$eventData.tool_input.notebookId
    }

    if ($null -ne $eventData.tool_input.query) {
        $query = [string]$eventData.tool_input.query
    }
}

if ([string]::IsNullOrWhiteSpace($notebookId)) {
    [Console]::Error.WriteLine(
        "QMind retrieve blocked by Windchill AI DevKit: notebookId is missing. Do not answer from model memory. Load qmind-enterprise-router, read references/qmind-registry.md, select the matching notebook, then retry retrieve with both notebookId and query."
    )
    exit 2
}

if ([string]::IsNullOrWhiteSpace($query)) {
    [Console]::Error.WriteLine(
        "QMind retrieve blocked by Windchill AI DevKit: query is missing. Build a focused Product / Framework knowledge query, then retry retrieve with both notebookId and query."
    )
    exit 2
}

exit 0