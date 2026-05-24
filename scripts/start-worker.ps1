# Run Celery worker
Set-Location "$PSScriptRoot\.."
$env:PYTHONPATH = "$PSScriptRoot\..\backend;$PSScriptRoot\.."
celery -A workers.celery_app worker --beat --loglevel=info --pool=solo
