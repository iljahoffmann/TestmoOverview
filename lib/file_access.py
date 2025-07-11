import os
import sys
import getpass
import subprocess


def restrict_to_owner(filename):
	"""
	Sets file permissions so that only the owner has full control (read/write).
	Works on both Windows and Unix-like systems.
	"""
	if os.name == 'nt':
		# Windows system
		username = getpass.getuser()
		# Remove inheritance
		subprocess.run(['icacls', filename, '/inheritance:r'], check=True)
		# Grant full control to the owner
		subprocess.run(['icacls', filename, f'/grant', f'{username}:F'], check=True)
		# Remove other users/groups (may not be present, so don't check returncode)
		subprocess.run(['icacls', filename, '/remove', 'Users'], check=False)
		subprocess.run(['icacls', filename, '/remove', 'Everyone'], check=False)
	else:
		# Unix/Linux/macOS
		# chmod 600 = owner read/write, no access for others
		os.chmod(filename, 0o600)

# Example usage:
# restrict_to_owner('secret.json')
