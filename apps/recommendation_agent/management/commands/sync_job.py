"""
Django management command to sync a specific job or jobs to Weaviate.

Usage:
    python manage.py sync_job 123                # Sync job ID 123
    python manage.py sync_job 123 456 789        # Sync multiple jobs
    python manage.py sync_job --delete 123       # Delete job ID 123 from Weaviate
"""
from django.core.management.base import BaseCommand, CommandError
from apps.recommendation_agent.services.job_service import JobIndexingService
from apps.recommendation_agent.services.weaviate_service import delete_job


class Command(BaseCommand):
    help = 'Sync specific job(s) between PostgreSQL and Weaviate'

    def add_arguments(self, parser):
        parser.add_argument(
            'job_ids',
            nargs='+',
            type=int,
            help='Job IDs to sync or delete',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete jobs from Weaviate instead of syncing',
        )

    def handle(self, *args, **options):
        job_ids = options.get('job_ids')
        delete_mode = options.get('delete', False)

        if delete_mode:
            # Delete jobs from Weaviate
            self.stdout.write(self.style.WARNING(
                f'\nDeleting {len(job_ids)} job(s) from Weaviate...\n'
            ))

            success_count = 0
            failed_count = 0

            for job_id in job_ids:
                if delete_job(job_id):
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted job {job_id}'))
                else:
                    failed_count += 1
                    self.stdout.write(self.style.ERROR(f'✗ Failed to delete job {job_id}'))

            self.stdout.write('\n' + '='*60)
            self.stdout.write(f"Total jobs processed: {len(job_ids)}")
            self.stdout.write(self.style.SUCCESS(f"✓ Successfully deleted: {success_count}"))
            if failed_count > 0:
                self.stdout.write(self.style.ERROR(f"✗ Failed to delete: {failed_count}"))
            self.stdout.write('='*60 + '\n')

        else:
            # Sync jobs to Weaviate
            self.stdout.write(self.style.WARNING(
                f'\nSyncing {len(job_ids)} job(s) to Weaviate...\n'
            ))

            success_count = 0
            failed_count = 0
            not_found_count = 0

            for job_id in job_ids:
                job = JobIndexingService.get_job_by_id(job_id)

                if not job:
                    not_found_count += 1
                    self.stdout.write(self.style.WARNING(
                        f'⚠ Job {job_id} not found in PostgreSQL'
                    ))
                    continue

                if job.status != 'approved':
                    self.stdout.write(self.style.WARNING(
                        f'⚠ Job {job_id} is not approved (status: {job.status}), skipping'
                    ))
                    continue

                if JobIndexingService.index_single_job(job):
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Synced job {job_id}: {job.title}'
                    ))
                else:
                    failed_count += 1
                    self.stdout.write(self.style.ERROR(
                        f'✗ Failed to sync job {job_id}'
                    ))

            self.stdout.write('\n' + '='*60)
            self.stdout.write(f"Total jobs requested: {len(job_ids)}")
            self.stdout.write(self.style.SUCCESS(f"✓ Successfully synced: {success_count}"))
            if failed_count > 0:
                self.stdout.write(self.style.ERROR(f"✗ Failed to sync: {failed_count}"))
            if not_found_count > 0:
                self.stdout.write(self.style.WARNING(f"⚠ Not found: {not_found_count}"))
            self.stdout.write('='*60 + '\n')
"""
Django management command to clean up Weaviate database.

Usage:
    python manage.py cleanup_weaviate --remove-duplicates    # Remove duplicate entries
    python manage.py cleanup_weaviate --sync                 # Sync with PostgreSQL
    python manage.py cleanup_weaviate --clear-all            # Clear all jobs (dangerous!)
"""
from django.core.management.base import BaseCommand, CommandError
from apps.recommendation_agent.services.weaviate_service import (
    remove_duplicates,
    sync_with_postgres,
    clear_all_jobs,
    get_job_count
)


class Command(BaseCommand):
    help = 'Clean up and synchronize Weaviate job index'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remove-duplicates',
            action='store_true',
            help='Remove duplicate job entries from Weaviate',
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Sync Weaviate with PostgreSQL (remove jobs that are not approved)',
        )
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Clear all jobs from Weaviate (WARNING: destructive operation)',
        )

    def handle(self, *args, **options):
        remove_dupes = options.get('remove_duplicates')
        sync = options.get('sync')
        clear_all = options.get('clear_all')

        if not any([remove_dupes, sync, clear_all]):
            raise CommandError(
                'Please specify an action: --remove-duplicates, --sync, or --clear-all'
            )

        # Show initial count
        self.stdout.write(self.style.WARNING('\nChecking Weaviate status...'))
        initial_count = get_job_count()
        self.stdout.write(f"Current job count: {initial_count}\n")

        # Clear all jobs (dangerous!)
        if clear_all:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  WARNING: This will delete ALL jobs from Weaviate!'
            ))
            confirm = input('Type "yes" to confirm: ')
            if confirm.lower() == 'yes':
                try:
                    clear_all_jobs()
                    self.stdout.write(self.style.SUCCESS(
                        '\n✓ All jobs cleared from Weaviate'
                    ))
                except Exception as e:
                    raise CommandError(f'Failed to clear jobs: {str(e)}')
            else:
                self.stdout.write(self.style.WARNING('Operation cancelled'))
                return

        # Remove duplicates
        if remove_dupes:
            self.stdout.write(self.style.WARNING(
                '\nRemoving duplicate entries from Weaviate...'
            ))
            try:
                result = remove_duplicates()

                if 'error' in result:
                    raise CommandError(f'Failed to remove duplicates: {result["error"]}')

                self.stdout.write('\n' + '='*60)
                self.stdout.write(self.style.SUCCESS('DUPLICATE REMOVAL RESULTS'))
                self.stdout.write('='*60)
                self.stdout.write(f"Total unique jobs: {result['total_jobs']}")
                self.stdout.write(f"Jobs with duplicates: {result['duplicates_found']}")
                self.stdout.write(self.style.SUCCESS(
                    f"✓ Duplicate entries deleted: {result['entries_deleted']}"
                ))
                self.stdout.write('='*60 + '\n')

            except Exception as e:
                raise CommandError(f'Failed to remove duplicates: {str(e)}')

        # Sync with PostgreSQL
        if sync:
            self.stdout.write(self.style.WARNING(
                '\nSynchronizing Weaviate with PostgreSQL...'
            ))
            try:
                result = sync_with_postgres()

                if 'error' in result:
                    raise CommandError(f'Failed to sync: {result["error"]}')

                self.stdout.write('\n' + '='*60)
                self.stdout.write(self.style.SUCCESS('SYNC RESULTS'))
                self.stdout.write('='*60)
                self.stdout.write(f"Jobs in Weaviate (before): {result['weaviate_jobs']}")
                self.stdout.write(f"Approved jobs in PostgreSQL: {result['postgres_jobs']}")
                self.stdout.write(self.style.SUCCESS(
                    f"✓ Outdated jobs deleted: {result['deleted']}"
                ))
                self.stdout.write(f"Jobs remaining in Weaviate: {result['remaining']}")
                self.stdout.write('='*60 + '\n')

            except Exception as e:
                raise CommandError(f'Failed to sync: {str(e)}')

        # Show final count
        self.stdout.write(self.style.WARNING('Final Weaviate status:'))
        final_count = get_job_count()
        self.stdout.write(f"Current job count: {final_count}")

        if initial_count != final_count:
            change = final_count - initial_count
            self.stdout.write(self.style.SUCCESS(
                f"Net change: {change:+d} jobs\n"
            ))

