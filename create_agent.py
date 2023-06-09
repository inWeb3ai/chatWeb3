"""
create_agent.py
This file sets up the agent executor for the chatbot application.
"""

import logging
import os

from langchain.callbacks.manager import CallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

from chatweb3.agents.agent_toolkits.snowflake.base import (
    create_snowflake_chat_agent, create_snowflake_conversational_chat_agent)
from chatweb3.agents.agent_toolkits.snowflake.prompt import (
    CUSTOM_CONV_SNOWFLAKE_PREFIX, CUSTOM_CONV_SNOWFLAKE_SUFFIX,
    CUSTOM_FORMAT_INSTRUCTIONS, CUSTOM_SNOWFLAKE_PREFIX,
    CUSTOM_SNOWFLAKE_SUFFIX)
from chatweb3.agents.agent_toolkits.snowflake.toolkit_custom import \
    CustomSnowflakeDatabaseToolkit
from chatweb3.callbacks.logger_callback import LoggerCallbackHandler
from chatweb3.snowflake_database import SnowflakeContainer
from config.config import agent_config
from config.logging_config import get_logger

logger = get_logger(
    __name__, log_level=logging.INFO, log_to_console=True, log_to_file=True
)

PROJ_ROOT_DIR = agent_config.get("proj_root_dir")
LOCAL_INDEX_FILE_PATH = os.path.join(
    PROJ_ROOT_DIR, agent_config.get("metadata.context_ethereum_core_file")
)
INDEX_ANNOTATION_FILE_PATH = os.path.join(
    PROJ_ROOT_DIR, agent_config.get("metadata.annotation_ethereum_core_file")
)
QUERY_DATABASE_TOOL_TOP_K = agent_config.get("tool.query_database_tool_top_k")
# AGENT_EXECUTOR_RETURN_INTERMEDIDATE_STEPS = agent_config.get(
#    "agent_chain.agent_executor_return_intermediate_steps"
# )


def create_agent_executor(conversation_mode=False):
    """
    Creates and returns an agent executor.

    Returns:
    agent_executor: The created agent executor
    """
    callbacks = CallbackManager([LoggerCallbackHandler()])

    llm = ChatOpenAI(
        model_name=agent_config.get("model.llm_name"),
        temperature=0,
        callbacks=callbacks,
        max_tokens=256,
        verbose=True,
    )

    snowflake_container_eth_core = SnowflakeContainer(
        **agent_config.get("snowflake_params")
        if agent_config.get("snowflake_params")
        else {},
        **agent_config.get("shroomdk_params")
        if agent_config.get("shroomdk_params")
        else {},
        local_index_file_path=LOCAL_INDEX_FILE_PATH,
        index_annotation_file_path=INDEX_ANNOTATION_FILE_PATH,
        verbose=False,
    )

    snowflake_toolkit = CustomSnowflakeDatabaseToolkit(
        db=snowflake_container_eth_core,
        llm=llm,
        readonly_shared_memory=None,
        verbose=True,
    )

    if conversation_mode:
        snowflake_toolkit.instructions = ""
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        agent_executor = create_snowflake_conversational_chat_agent(
            llm=llm,
            toolkit=snowflake_toolkit,
            prefix=CUSTOM_CONV_SNOWFLAKE_PREFIX,
            suffix=CUSTOM_CONV_SNOWFLAKE_SUFFIX,
            format_instructions=CUSTOM_FORMAT_INSTRUCTIONS,
            memory=memory,
            return_intermediate_steps=False,
            top_k=QUERY_DATABASE_TOOL_TOP_K,
            max_iterations=15,
            max_execution_time=300,
            early_stopping_method="force",
            callbacks=callbacks,
            verbose=True,
        )

    else:
        agent_executor = create_snowflake_chat_agent(
            llm=llm,
            toolkit=snowflake_toolkit,
            prefix=CUSTOM_SNOWFLAKE_PREFIX,
            suffix=CUSTOM_SNOWFLAKE_SUFFIX,
            format_instructions=CUSTOM_FORMAT_INSTRUCTIONS,
            return_intermediate_steps=True,
            top_k=QUERY_DATABASE_TOOL_TOP_K,
            max_iterations=15,
            max_execution_time=300,
            early_stopping_method="generate",
            callbacks=callbacks,
            verbose=True,
        )

    return agent_executor
