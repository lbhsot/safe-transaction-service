# Generated by Django 3.0.8 on 2020-07-28 11:14

from django.db import migrations, models

from ..indexers.tx_processor import SafeTxProcessor, SafeTxProcessorProvider


def set_failed_for_module_txs(apps, schema_editor):
    safe_tx_processor: SafeTxProcessor = SafeTxProcessorProvider()
    ModuleTransaction = apps.get_model('history', 'ModuleTransaction')
    for module_tx in ModuleTransaction.objects.select_related('internal_tx__ethereum_tx').iterator():
        current_failed = module_tx.failed
        module_tx.failed = safe_tx_processor.is_module_failed(module_tx.internal_tx.ethereum_tx, module_tx.module,
                                                              module_tx.safe)
        if module_tx.failed != current_failed:
            module_tx.save(update_fields=['failed'])


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0020_safemastercopy_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='moduletransaction',
            name='failed',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_failed_for_module_txs, reverse_code=migrations.RunPython.noop),
    ]
