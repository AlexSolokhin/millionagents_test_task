class CloudError(Exception):
    pass


class CloudAuthError(CloudError):
    pass


class CloudFileUploadError(CloudError):
    pass