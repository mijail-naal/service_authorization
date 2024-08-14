from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from core.config import settings


def configure_tracer() -> None:
    # https://opentelemetry.io/docs/languages/python/cookbook/

    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: settings.service_name})
        )
    )

    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger_host,
                agent_port=settings.jaeger_port,
            )
        )
    )

    # Uncomment the next lines to show the trace in console.
    # trace.get_tracer_provider().add_span_processor(
    #     BatchSpanProcessor(
    #         ConsoleSpanExporter()
    #     )
    # )
