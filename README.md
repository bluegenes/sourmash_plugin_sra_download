# sourmash_plugin_sra_download

## Installation

Current (dev only):


```
git clone https://github.com/sourmash-bio/sourmash_plugin_sra_download.git
cd sourmash_plugin_sra_download
pip install -e '.'

#future: pip install sourmash_plugin_sra_download
```

## Usage

```
sourmash scripts sra_download --help
```

```
usage:  sra_download [-h] [-q] [-d] [--output-dir OUTPUT_DIR] [--download-only] [--delete-fastq] [-m {ena-ftp,aws-http,prefetch,aws-cp,gcp-cp,ena_ascp} [{ena-ftp,aws-http,prefetch,aws-cp,gcp-cp,ena_ascp} ...]]
                     [-t THREADS] [--sig-extension SIG_EXTENSION] [--verbose] [-p PARAM_STRING]
                     sra_accession [sra_accession ...]

positional arguments:
  sra_accession

options:
  -h, --help            show this help message and exit
  -q, --quiet           suppress non-error output
  -d, --debug           provide debugging output
  --output-dir OUTPUT_DIR
  --download-only       Only download SRA file(s) and do not sketch.
  --delete-fastq        Delete fastq file(s) after sketching.
  -m {ena-ftp,aws-http,prefetch,aws-cp,gcp-cp,ena_ascp} [{ena-ftp,aws-http,prefetch,aws-cp,gcp-cp,ena_ascp} ...], --download-methods {ena-ftp,aws-http,prefetch,aws-cp,gcp-cp,ena_ascp} [{ena-ftp,aws-http,prefetch,aws-cp,gcp-cp,ena_ascp} ...]
  -t THREADS, --threads THREADS
                        Number of threads to use for download and conversion to fastq.
  --sig-extension SIG_EXTENSION
                        sourmash signature file extension to use.
  --verbose             Print verbose output.
  -p PARAM_STRING, --param-string PARAM_STRING
                        sourmash signature parameters to use.

```

## Support

We suggest filing issues in [the main sourmash issue tracker](https://github.com/dib-lab/sourmash/issues) as that receives more attention!

## Dev docs

`sra_download` is developed at https://github.com/sourmash-bio/sourmash_plugin_sra_download.

### Generating a release

Bump version number in `pyproject.toml` and push.

Make a new release on github.

Then pull, and:

```
python -m build
```

followed by `twine upload dist/...`.
