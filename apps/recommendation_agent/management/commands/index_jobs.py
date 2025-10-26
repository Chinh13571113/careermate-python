"""
Django management command to index jobs from PostgreSQL into Weaviate.

Usage:
    python manage.py index_jobs                    # Index all active jobs
    python manage.py index_jobs --limit 100        # Index first 100 jobs
    python manage.py index_jobs --all              # Include inactive jobs
    python manage.py index_jobs --job-ids 1 2 3    # Index specific jobs
"""
from django.core.management.base import BaseCommand, CommandError
from apps.recommendation_agent.services.job_service import JobIndexingService


class Command(BaseCommand):
    help = 'Index jobs from PostgreSQL into Weaviate for content-based recommendations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of jobs to index',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Include inactive jobs (default: only active)',
        )
        parser.add_argument(
            '--job-ids',
            nargs='+',
            type=int,
            help='Specific job IDs to index',
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        only_active = not options.get('all', False)
        job_ids = options.get('job_ids')

        self.stdout.write(self.style.WARNING('Starting job indexing process...'))

        # Validate PostgreSQL connection
        try:
            from django.db import connections
            with connections['postgres'].cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('✓ PostgreSQL connection successful'))
        except Exception as e:
            raise CommandError(f'Failed to connect to PostgreSQL: {str(e)}')

        # Perform bulk indexing
        try:
            result = JobIndexingService.bulk_index_jobs(
                limit=limit,
                only_active=only_active,
                job_ids=job_ids
            )

            # Display results
            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('INDEXING RESULTS'))
            self.stdout.write('='*60)
            self.stdout.write(f"Total jobs processed: {result['total']}")
            self.stdout.write(self.style.SUCCESS(f"✓ Successfully indexed: {result['success']}"))

            if result['failed'] > 0:
                self.stdout.write(self.style.ERROR(f"✗ Failed to index: {result['failed']}"))
                self.stdout.write(f"Failed job IDs: {result['failed_job_ids']}")
            else:
                self.stdout.write(self.style.SUCCESS('✓ All jobs indexed successfully!'))

            self.stdout.write('='*60 + '\n')

        except Exception as e:
            raise CommandError(f'Indexing failed: {str(e)}')
# This file makes the management directory a Python package

