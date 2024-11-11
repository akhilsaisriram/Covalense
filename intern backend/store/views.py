
from django.shortcuts import render
import tarfile
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Exempt CSRF protection
from django.views.decorators.http import require_http_methods
from .models import LogEntry  # Assuming the LogEntry model is in the same app

@csrf_exempt  # Exempt CSRF protection for this view
@require_http_methods(["GET", "POST"])
def process_tgz(request):
    if request.method != 'POST' or 'file' not in request.FILES:
        return JsonResponse({'error': 'Please upload a .tgz file'}, status=400)
    
    tgz_file = request.FILES['file']
    results = []
    ignored_lines = []  # List to capture ignored lines due to invalid UTF-8
    
    try:
        file_content = io.BytesIO(tgz_file.read())
        
        # Process the TGZ file directly from memory
        with tarfile.open(fileobj=file_content, mode='r:gz') as tar:
            # List to hold LogEntry instances for bulk insert
            log_entries = []
            
            # Iterate through each file in the archive
            for member in tar.getmembers():
                if member.isfile():  # Process only files, not directories
                    try:
                        # Extract file content directly to memory
                        file_data = tar.extractfile(member)
                        if file_data:
                            # Try reading and decoding the content (ignore invalid UTF-8 characters)
                            try:
                                content = file_data.read().decode('utf-8')
                            except UnicodeDecodeError as e:
                                # If decoding fails, capture the error and add to ignored_lines
                                ignored_lines.append({
                                    'filename': member.name,
                                    'error': f'UnicodeDecodeError: {str(e)}',
                                    'line': file_data.read().decode('utf-8', errors='ignore')  # Capture ignored content
                                })
                                continue  # Skip this file if decoding fails
                            
                            lines = content.splitlines()
                            
                            # Process the lines
                            for line in lines:
                                # Split the line into components based on your data format
                                parts = line.strip().split()
                                if len(parts) >= 14:  # Ensure we have all expected fields
                                    try:
                                        # Create LogEntry object
                                        log_entry = LogEntry(
                                            serialno=int(parts[0]),
                                            version=int(parts[1]),
                                            account_id=int(parts[10]),
                                            instance_id=parts[3],
                                            srcaddr=parts[4],
                                            dstaddr=parts[5],
                                            srcport=int(parts[6]),
                                            dstport=int(parts[7]),
                                            protocol=int(parts[8]),
                                            packets=int(parts[9]),
                                            bytes=int(parts[9]),
                                            starttime=int(parts[11]),
                                            endtime=int(parts[12]),
                                            action=parts[13],
                                            log_status=parts[14] if len(parts) > 14 else 'UNKNOWN'
                                        )
                                        log_entries.append(log_entry)
                                    except ValueError as e:
                                        # Handle invalid data type conversion gracefully
                                        results.append({
                                            'filename': member.name,
                                            'line': line,
                                            'error': f'Invalid data in line: {str(e)}'
                                        })
            
                    except Exception as e:
                                # Handle the exception here
                                return JsonResponse({
                                    'status': 'error',
                                    'message': f'Error processing TGZ file: {str(e)}'
                                }, status=500)
            # Perform bulk insert if there are any valid log entries
            if log_entries:
                LogEntry.objects.bulk_create(log_entries)
            
            # Return the processed data
            results.append({
                'status': 'success',
                'files_processed': len(tar.getmembers()),
                'valid_entries': len(log_entries),
                'errors': len(results),
                'ignored_lines': ignored_lines  # Include ignored lines due to decoding issues
            })
                        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error processing TGZ file: {str(e)}'
        }, status=500)
    
    return JsonResponse({
        'status': 'success',
        'files_processed': len(results),
        'results': results,
        'ignored_lines': ignored_lines  # Send ignored lines with details
    })



from django.db.models import Q
from .models import LogEntry

@csrf_exempt
def search_logs(request):
    # Get parameters from request
    searchstring = request.GET.get('searchstring', '')
    earliest_time = request.GET.get('EarliestTime', None)
    latest_time = request.GET.get('LatestTime', None)

    # Initialize the filters
    filters = Q()
    params = []

    # Parse the searchstring into key-value pairs for dynamic filtering
    if searchstring:
        search_params = searchstring.split(',')
        for param in search_params:
            key, value = param.split('=')
            if key == 'account_id':
                filters &= Q(account_id=value)
                params.append(value)
            elif key == 'instance_id':
                filters &= Q(instance_id=value)
                params.append(value)
            elif key == 'srcaddr':
                filters &= Q(srcaddr=value)
                params.append(value)
            elif key == 'dstaddr':
                filters &= Q(dstaddr=value)
                params.append(value)
            elif key == 'srcport':
                filters &= Q(srcport=value)
                params.append(value)
            elif key == 'dstport':
                filters &= Q(dstport=value)
                params.append(value)

    # Efficient handling of time-based filtering
    if earliest_time:
        try:
            earliest_time = int(earliest_time)
            filters &= Q(starttime__gte=earliest_time)
            params.append(earliest_time)
        except ValueError:
            return JsonResponse({'error': 'EarliestTime must be an integer'}, status=400)

    if latest_time:
        try:
            latest_time = int(latest_time)
            filters &= Q(endtime__lte=latest_time)
            params.append(latest_time)
        except ValueError:
            return JsonResponse({'error': 'LatestTime must be an integer'}, status=400)

    # Build the query string dynamically using the filters
    query = LogEntry.objects.filter(filters)

    # Execute the query using the dynamically constructed filter
    log_entries = query.values('serialno', 'version', 'account_id', 'instance_id', 'srcaddr', 'dstaddr', 'srcport', 'dstport', 'protocol', 'packets', 'bytes', 'starttime', 'endtime', 'action', 'log_status')

    # Serialize the results
    results = []
    for entry in log_entries:
        # print(entry)
        results.append({
            'serialno': entry['serialno'],
            'version': entry['version'],
            'account_id': entry['account_id'],
            'instance_id': entry['instance_id'],
            'srcaddr': entry['srcaddr'],
            'dstaddr': entry['dstaddr'],
            'srcport': entry['srcport'],
            'dstport': entry['dstport'],
            'protocol': entry['protocol'],
            'packets': entry['packets'],
            'bytes': entry['bytes'],
            'starttime': entry['starttime'],
            'endtime': entry['endtime'],
            'action': entry['action'],
            'log_status': entry['log_status']
        })
    print(len(results))
    return JsonResponse({'status': 'success', 'results': results})
