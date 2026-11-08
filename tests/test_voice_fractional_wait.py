"""Exercise fractional waits when the image's sleep accepts only integers."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from helpers import TOP


class FractionalWait(unittest.TestCase):
    def test_static_busybox_preserves_requested_duration(self):
        source = (TOP / "device/bin/mu300-voice").read_text()
        block = source[source.index("if sleep 0.01"):source.index("\nat()")]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sleep = root / "sleep"
            sleep.write_text("#!/bin/sh\nexit 1\n")
            sleep.chmod(0o755)
            busybox = root / "busybox"
            busybox.write_text(
                '#!/bin/sh\n[ "$1" = sleep ] || exit 2\n'
                'printf "%s\\n" "$2" >> "$WAIT_LOG"\n'
            )
            busybox.chmod(0o755)
            block = block.replace("/opt/mu300/bin/busybox", str(busybox))
            log = root / "wait.log"
            environment = dict(os.environ, PATH=str(root), WAIT_LOG=str(log))
            subprocess.run(
                ["/bin/sh", "-ec", block + "\nnap 0.1\nnap 0.5\n"],
                env=environment, check=True,
            )
            self.assertEqual(log.read_text().splitlines(), ["0.01", "0.1", "0.5"])


if __name__ == "__main__":
    unittest.main()
