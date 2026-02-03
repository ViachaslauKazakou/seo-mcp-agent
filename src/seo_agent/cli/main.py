"""CLI entry point for SEO Agent."""

import asyncio
import click
import json
from typing import List

from seo_agent.models import InputSpec
from seo_agent.api.agent import SEOAgent


@click.group()
def cli():
    """SEO Agent CLI."""
    pass


@cli.command()
@click.option("--url", "-u", multiple=True, required=True, help="URLs to analyze")
@click.option("--output", "-o", type=click.Path(), help="Output file (JSON)")
@click.option("--depth", "-d", type=int, default=0, help="Crawl depth")
@click.option("--max-pages", "-m", type=int, default=50, help="Max pages to analyze")
@click.option("--use-openai", is_flag=True, default=False, help="Use OpenAI for recommendations")
@click.option("--openai-model", type=str, default="gpt-4o-mini", help="OpenAI model name")
@click.option("--hf-model", type=str, default="all-MiniLM-L6-v2", help="HuggingFace embedding model")
@click.option("--embedding-provider", type=click.Choice(["hf", "openai"]), default="hf", help="Embedding provider")
@click.option("--openai-embedding-model", type=str, default="text-embedding-3-small", help="OpenAI embedding model")
def analyze(url: tuple, output: str, depth: int, max_pages: int, use_openai: bool, openai_model: str, hf_model: str, embedding_provider: str, openai_embedding_model: str):
    """Analyze URLs for SEO."""
    if not url:
        click.echo("Error: At least one URL required", err=True)
        return
    
    click.echo(f"🔍 Analyzing {len(url)} URL(s)...")
    click.echo(f"   Embeddings: {embedding_provider}")
    if embedding_provider == "hf":
        click.echo(f"   HF Model: {hf_model}")
    else:
        click.echo(f"   OpenAI Embedding Model: {openai_embedding_model}")
    
    # Create input spec
    input_spec = InputSpec(
        urls=list(url),
        max_depth=depth,
        max_pages=max_pages,
        use_openai=use_openai,
        openai_model=openai_model,
        hf_embedding_model=hf_model,
        embedding_provider=embedding_provider,
        openai_embedding_model=openai_embedding_model,
    )
    
    # Run analysis
    agent = SEOAgent()
    report = asyncio.run(agent.analyze(input_spec))
    
    # Display results
    click.echo("\n✅ Analysis complete!")
    click.echo(f"📄 Documents parsed: {report.documents_parsed}")
    click.echo(f"🔑 Keywords found: {len(report.keywords_extracted)}")
    click.echo(f"📊 Clusters: {len(report.clusters)}")
    click.echo(f"💡 Recommendations: {len(report.recommendations)}")
    
    if report.errors:
        click.echo(f"\n⚠️ Errors ({len(report.errors)}):")
        for error in report.errors:
            click.echo(f"  - {error}")
    
    # Save output if requested
    if output:
        with open(output, "w") as f:
            json.dump(report.model_dump(), f, indent=2, default=str)
        click.echo(f"\n💾 Saved to {output}")
    else:
        # Print summary
        click.echo("\n📋 Top Keywords:")
        for kw in report.keywords_extracted[:5]:
            click.echo(f"  - {kw.keyword} (score: {kw.tf_idf_score:.3f})")
        
        click.echo("\n📊 Top Recommendations:")
        for rec in report.recommendations[:3]:
            click.echo(f"  [{rec.priority}/5] {rec.title}")


@cli.command()
def server():
    """Start FastAPI server."""
    import uvicorn
    click.echo("🚀 Starting SEO Agent API on http://127.0.0.1:8000")
    uvicorn.run("seo_agent.api.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    cli()
