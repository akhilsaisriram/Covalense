from django.db import models

class LogEntry(models.Model):
    serialno = models.IntegerField()  # Serial number (integer)
    version = models.IntegerField()  # Version (integer)
    account_id = models.BigIntegerField()  # Account ID (big integer for large numbers)
    instance_id = models.CharField(max_length=255)  # Instance ID (string)
    srcaddr = models.GenericIPAddressField()  # Source IP address (IPv4 or IPv6)
    dstaddr = models.GenericIPAddressField()  # Destination IP address (IPv4 or IPv6)
    srcport = models.IntegerField()  # Source port (integer)
    dstport = models.IntegerField()  # Destination port (integer)
    protocol = models.IntegerField()  # Protocol (integer)
    packets = models.IntegerField()  # Number of packets (integer)
    bytes = models.IntegerField()  # Number of bytes (integer)
    starttime = models.BigIntegerField()  # Start time (big integer, Unix timestamp)
    endtime = models.BigIntegerField()  # End time (big integer, Unix timestamp)
    action = models.CharField(max_length=50)  # Action (string, e.g., REJECT or ACCEPT)
    log_status = models.CharField(max_length=50)  # Log status (string, e.g., OK or FAIL)

    # def __str__(self):
    #     return f"LogEntry {self.serialno} - {self.action}"

    # class Meta:
    #     verbose_name = 'Log Entry'
    #     verbose_name_plural = 'Log Entries'
