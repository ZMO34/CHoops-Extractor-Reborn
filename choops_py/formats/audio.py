from ..archive.manifests import digest
def inspect(data):return dict(mode='raw preservation only',size=len(data),sha256=digest(data),prefix_hex=data[:64].hex(),codec='unknown; no transcode')
