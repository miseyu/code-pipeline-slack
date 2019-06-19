# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import boto3
import time

# from test_events import TEST_EVENTS, TEST_ERROR_EVENTS
from build_info import BuildInfo, CodeBuildInfo
from slack_helper import post_build_msg, find_message_for_build
from message_builder import MessageBuilder

# import re
# import sys

client = boto3.client("codepipeline")


def find_revision_info(info):
    r = client.get_pipeline_execution(
        pipelineName=info.pipeline, pipelineExecutionId=info.executionId
    )["pipelineExecution"]

    revs = r.get("artifactRevisions", [])
    if len(revs) > 0:
        return revs[0]
    return None


def pipeline_from_build(codeBuildInfo):
    r = client.get_pipeline_state(name=codeBuildInfo.pipeline)

    for s in r["stageStates"]:
        for a in s["actionStates"]:
            executionId = a.get("latestExecution", {}).get("externalExecutionId")
            if executionId and codeBuildInfo.buildId.endswith(executionId):
                pe = s["latestExecution"]["pipelineExecutionId"]
                return (s["stageName"], pe, a)

    return (None, None, None)


def process_code_pipeline(event):
    buildInfo = BuildInfo.from_event(event)
    existing_msg = find_message_for_build(buildInfo)
    builder = MessageBuilder(buildInfo, existing_msg)
    builder.update_pipeline_event(event)

    if builder.needs_revision_info():
        revision = find_revision_info(buildInfo)
        builder.attach_revision_info(revision)

    post_build_msg(builder)


def process_code_build(event):
    cbi = CodeBuildInfo.from_event(event)
    (stage, pid, actionStates) = pipeline_from_build(cbi)

    if not pid:
        return

    buildInfo = BuildInfo(pid, cbi.pipeline)

    existing_msg = find_message_for_build(buildInfo)
    builder = MessageBuilder(buildInfo, existing_msg)

    if "phases" in event["detail"]["additional-information"]:
        phases = event["detail"]["additional-information"]["phases"]
        builder.update_build_stage_info(stage, phases, actionStates)

    logs = event["detail"].get("additional-information", {}).get("logs")
    if logs:
        builder.attach_logs(event["detail"]["additional-information"]["logs"])

    post_build_msg(builder)


def process(event):
    if event["source"] == "aws.codepipeline":
        process_code_pipeline(event)
    if event["source"] == "aws.codebuild":
        process_code_build(event)


def run(event, context):
    m = process(event)


if __name__ == "__main__":
    with open("test-event.json") as f:
        events = json.load(f)
        for e in events:
            run(e, {})
            time.sleep(1)
