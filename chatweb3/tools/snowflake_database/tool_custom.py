"""
tool_custom.py
This file contains the custom tools for the snowflake_database toolkit.
"""
from typing import Any, List, Optional, Union

from langchain.callbacks.manager import CallbackManagerForToolRun

from chatweb3.tools.snowflake_database.tool import (
    GetSnowflakeDatabaseTableMetadataTool,
    ListSnowflakeDatabaseTableNamesTool,
    QuerySnowflakeDatabaseTool,
    SnowflakeQueryCheckerTool,
)

from chatweb3.tools.snowflake_database.constants import (
    CHECK_QUERY_SYNTAX_TOOL_NAME,
    CHECK_TABLE_METADATA_TOOL_NAME,
    CHECK_TABLE_SUMMARY_TOOL_NAME,
    QUERY_DATABASE_TOOL_NAME,
)
from config.config import agent_config

QUERY_DATABASE_TOOL_MODE = agent_config.get("tool.query_database_tool_mode")
CHECK_TABLE_SUMMARY_TOOL_MODE = agent_config.get("tool.check_table_summary_tool_mode")
CHECK_TABLE_METADATA_TOOL_MODE = agent_config.get("tool.check_table_metadata_tool_mode")

# CHECK_TABLE_SUMMARY_TOOL_NAME = "check_available_tables_summary"
# CHECK_TABLE_METADATA_TOOL_NAME = "check_table_metadata_details"
# CHECK_QUERY_SYNTAX_TOOL_NAME = "check_snowflake_query_syntax"
# QUERY_DATABASE_TOOL_NAME = "query_snowflake_database"


class CheckTableSummaryTool(ListSnowflakeDatabaseTableNamesTool):
    name = CHECK_TABLE_SUMMARY_TOOL_NAME
    description = """
    Input is an empty string.
    Output is the list of available tables in their full names (database.schema.table), accompanied by their summary descriptions to help you understand what each table is about.
    """

    def _run(  # type: ignore[override]
        self,
        tool_input: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
        mode: str = CHECK_TABLE_SUMMARY_TOOL_MODE,
    ) -> str:
        return super()._run(tool_input=tool_input, run_manager=run_manager, mode=mode)


class CheckTableMetadataTool(GetSnowflakeDatabaseTableMetadataTool):
    name = CHECK_TABLE_METADATA_TOOL_NAME
    description = """
    Input is one or more table names specified in their full names (database.schema.table) and seperated by a COMMA.
    Output is the detailed metadata including column specifics of those tables so that you can construct SQL query to them.
    """

    def _run(self, table_names: str, run_manager: Optional[CallbackManagerForToolRun] = None, mode: str = CHECK_TABLE_METADATA_TOOL_MODE) -> str:  # type: ignore[override]
        return super()._run(table_names=table_names, run_manager=run_manager, mode=mode)


class CheckQuerySyntaxTool(SnowflakeQueryCheckerTool):
    name = CHECK_QUERY_SYNTAX_TOOL_NAME
    description = """
    Input is a Snowflake SQL query.
    Output is the syntax check result of the query.
    """

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        return super()._run(query=query, run_manager=run_manager)


class QueryDatabaseTool(QuerySnowflakeDatabaseTool):
    name = QUERY_DATABASE_TOOL_NAME
    description = """
    Input to this tool contains a Snowflake SQL query in correct syntax. It should be in JSON format with EXACTLY ONE key "query" that has the value of the query string.
    Output is the query result from the database.
    """

    def _run(  # type: ignore[override]
        self,
        *args,
        mode: str = QUERY_DATABASE_TOOL_MODE,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs,
    ) -> Union[str, List[Any]]:
        return super()._run(*args, mode=mode, run_manager=run_manager, **kwargs)


# TOOLKIT_INSTRUCTIONS = f"""
# IMPORTANT:
# 1. Assistant must ALWAYS check available tables first! That is, NEVER EVER start with checking metadata tools or query database tools, ALWAYS start with the tool that tells you what tables are available in the database.
# 2. Before generating ANY query, assistant MUST first check the metadata of the table the query will be run against. NEVER EVER generate a query without checking the metadata of the table first.
# 3. If the assistant checked the tables in the database and found no table is related to the the human's specific question, assistant MUST NOT generate any queries, and MUST respond 'I don't know' as the answer, and ask the human to provide more information.
# """
