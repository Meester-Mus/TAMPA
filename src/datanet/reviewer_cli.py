#!/usr/bin/env python3
"""
Reviewer CLI

Command-line interface for reviewing pending decisions.
"""

import click
import json
from pathlib import Path
from typing import Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.datanet.decision_composer import DecisionComposer
from src.datanet.storage import get_storage


@click.group()
@click.pass_context
def cli(ctx):
    """TAMPA Datanet Agent - Reviewer CLI"""
    ctx.ensure_object(dict)
    ctx.obj['composer'] = DecisionComposer()
    ctx.obj['storage'] = get_storage(storage_type="local", base_path="./data")


@cli.command()
@click.pass_context
def list_pending(ctx):
    """List all pending reviews."""
    composer = ctx.obj['composer']
    
    # Load pending reviews from storage
    storage = ctx.obj['storage']
    proposal_keys = storage.list_keys(prefix="proposal_")
    
    pending = []
    for key in proposal_keys:
        proposal = storage.retrieve(key)
        if proposal and proposal.get('metadata', {}).get('status') == 'pending_review':
            pending.append(proposal)
    
    if not pending:
        click.echo("No pending reviews.")
        return
    
    click.echo(f"\n{'='*80}")
    click.echo(f"Pending Reviews ({len(pending)})")
    click.echo(f"{'='*80}\n")
    
    for i, record in enumerate(pending, 1):
        click.echo(f"[{i}] Record ID: {record.get('record_id')}")
        click.echo(f"    Type: {record.get('decision_type')}")
        click.echo(f"    Author: {record.get('author')}")
        click.echo(f"    Timestamp: {record.get('timestamp')}")
        click.echo(f"    Rationale: {record.get('rationale')}")
        click.echo()


@cli.command()
@click.argument('record_id')
@click.pass_context
def show(ctx, record_id: str):
    """Show details of a specific review record."""
    storage = ctx.obj['storage']
    
    record = storage.retrieve(f"proposal_{record_id}")
    if not record:
        click.echo(f"Error: Record {record_id} not found.", err=True)
        return
    
    click.echo("\n" + "="*80)
    click.echo("Decision Record Details")
    click.echo("="*80 + "\n")
    click.echo(json.dumps(record, indent=2))
    click.echo()


@cli.command()
@click.argument('record_id')
@click.option('--reviewer', required=True, help='Reviewer name')
@click.pass_context
def approve(ctx, record_id: str, reviewer: str):
    """Approve a pending review."""
    storage = ctx.obj['storage']
    
    record = storage.retrieve(f"proposal_{record_id}")
    if not record:
        click.echo(f"Error: Record {record_id} not found.", err=True)
        return
    
    if record.get('metadata', {}).get('status') != 'pending_review':
        click.echo(f"Error: Record is not pending review.", err=True)
        return
    
    # Update record
    from datetime import datetime
    record['metadata']['status'] = 'approved'
    record['metadata']['reviewer'] = reviewer
    record['metadata']['review_timestamp'] = datetime.utcnow().isoformat() + 'Z'
    
    storage.store(f"proposal_{record_id}", record)
    
    click.echo(f"✓ Record {record_id} approved by {reviewer}")


@cli.command()
@click.argument('record_id')
@click.option('--reviewer', required=True, help='Reviewer name')
@click.option('--reason', required=True, help='Rejection reason')
@click.pass_context
def reject(ctx, record_id: str, reviewer: str, reason: str):
    """Reject a pending review."""
    storage = ctx.obj['storage']
    
    record = storage.retrieve(f"proposal_{record_id}")
    if not record:
        click.echo(f"Error: Record {record_id} not found.", err=True)
        return
    
    if record.get('metadata', {}).get('status') != 'pending_review':
        click.echo(f"Error: Record is not pending review.", err=True)
        return
    
    # Update record
    from datetime import datetime
    record['metadata']['status'] = 'rejected'
    record['metadata']['reviewer'] = reviewer
    record['metadata']['rejection_reason'] = reason
    record['metadata']['review_timestamp'] = datetime.utcnow().isoformat() + 'Z'
    
    storage.store(f"proposal_{record_id}", record)
    
    click.echo(f"✗ Record {record_id} rejected by {reviewer}")
    click.echo(f"  Reason: {reason}")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show review statistics."""
    storage = ctx.obj['storage']
    
    proposal_keys = storage.list_keys(prefix="proposal_")
    
    pending = 0
    approved = 0
    rejected = 0
    
    for key in proposal_keys:
        proposal = storage.retrieve(key)
        if proposal:
            status = proposal.get('metadata', {}).get('status')
            if status == 'pending_review':
                pending += 1
            elif status == 'approved':
                approved += 1
            elif status == 'rejected':
                rejected += 1
    
    click.echo("\n" + "="*40)
    click.echo("Review Statistics")
    click.echo("="*40)
    click.echo(f"Pending:  {pending}")
    click.echo(f"Approved: {approved}")
    click.echo(f"Rejected: {rejected}")
    click.echo(f"Total:    {len(proposal_keys)}")
    click.echo()


if __name__ == '__main__':
    cli(obj={})
