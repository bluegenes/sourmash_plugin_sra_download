"""sra_download plugin description"""

usage="""
   sourmash scripts sra_download
"""

epilog="""
See https://github.com/sra_download for more examples.

Need help? Have questions? Ask at http://github.com/sourmash/issues!
"""

import os
import argparse
import sourmash
import subprocess
import screed

from sourmash.index import LinearIndex
from sourmash.command_sketch import _signatures_for_sketch_factory
from sourmash.command_compute import add_seq, set_sig_name
from sourmash.logging import debug_literal, notify, error
from sourmash.plugins import CommandLinePlugin
from sourmash import sourmash_args


###

#
# CLI plugin - supports 'sourmash scripts sra_download'
#

class Command_sra_download(CommandLinePlugin):
    command = 'sra_download'             # 'scripts <command>'
    description = __doc__       # output with -h
    usage = usage               # output with no args/bad args as well as -h
    epilog = epilog             # output with -h
    formatter_class = argparse.RawTextHelpFormatter # do not reformat multiline

    def __init__(self, subparser):
        super().__init__(subparser)
        # add argparse arguments here.
        debug_literal('RUNNING cmd_sra_download.__init__')
        subparser.add_argument('sra_accession', nargs='+')
        subparser.add_argument('--output-dir', default='.')
        subparser.add_argument('--download-only', action='store_true', default=False, help="Only download SRA file(s) and do not sketch.")
        subparser.add_argument('--delete-fastq', action='store_true', default=False, help="Delete fastq file(s) after sketching.")
        subparser.add_argument('-m', '--download-methods', default=['ena-ftp', 'aws-http', 'prefetch'], nargs='+', choices=['ena-ftp', 'aws-http', 'prefetch', 'aws-cp', 'gcp-cp', 'ena_ascp'])
        subparser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads to use for download and conversion to fastq.')
        subparser.add_argument('--sig-extension', default='zip', help='sourmash signature file extension to use.')
        subparser.add_argument('--verbose', action='store_true', default=False, help='Print verbose output.')
        subparser.add_argument('-p', '--param-string', default=[], help='sourmash signature parameters to use.', action='append')

    def download_sra(self, sra_accession, outdir, threads=1, download_methods = ['ena-ftp', 'aws-http', 'prefetch'], verbose=False):
        # run this kingfisher command via subprocess: kingfisher get -r ERR1739691 -m ena-ascp aws-http prefetch
        if verbose:
            print(f"Downloading {sra_accession} to {outdir}")
            # print kingfisher command:
            print(f"kingfisher get -t {threads} -r {sra_accession} -m {' '.join(download_methods)}")
        subprocess.run(['kingfisher', 'get', '-t', str(threads), '-r', sra_accession, '-m'] + download_methods, cwd=outdir)
        # Check if the downloaded file(s) exist
        downloaded_files = []
        potential_files = [f"{sra_accession}.fastq.gz", f"{sra_accession}_1.fastq.gz", f"{sra_accession}_2.fastq.gz"]
        for file in potential_files:
            # check if file exists and add to list if yes
            if os.path.exists(os.path.join(outdir, file)):
                downloaded_files.append(file)
        if len(downloaded_files) == 0:
            raise FileNotFoundError(f"Could not find downloaded file for {sra_accession}")
        else:
            if verbose:
                print(f"Found downloaded files for {sra_accession}: {downloaded_files}")
            return downloaded_files

    def sketch_sig(self, factories, fq_files, name, sigfile, *, verbose=False):
        # based on compute_sig in sketchall plugin
        "Build a set of sketches for the given filename."
        if verbose:
            notify(f"sketching '{fq_files}' => '{sigfile}'")

        sigslist = [ f() for f in factories ]
        # read sequences, build sketches
        try:
            for filename in fq_files:
                with screed.open(filename) as screed_iter:
                    if not screed_iter:
                        notify(f"no sequences found in '{filename}'; skipping.")
                        return None

                    for n, record in enumerate(screed_iter):
                        if n % 10000 == 0:
                            if n and verbose:
                                notify('\r...{} {}', filename, n, end='')

                        try:
                            for sigs in sigslist:
                                add_seq(sigs, record.sequence, False, False)
                        except ValueError as exc:
                            error(f"ERROR when reading from '{filename}' - ")
                            error(str(exc))
                            return None

                    if verbose:
                        notify('...{} {} sequences', filename, n + 1)

        except ValueError:
            return None
        
        # save sketches
        with sourmash_args.SaveSignaturesToLocation(sigfile) as save_sig:
            for sigs in sigslist:
                set_sig_name(sigs, filename, name)
                for ss in sigs:
                    save_sig.add(ss)

        debug_literal(f'saved {len(save_sig)} sketch(es) for {filename} to {sigfile}')
        return len(save_sig)


    def main(self, args):
        # code that we actually run.
        super().main(args)
        print('RUNNING cmd', self, args)
        
        # build params obj & sketching factories
        factories = []
        if not args.param_string:
            args.param_string.append('dna')
        for p in args.param_string:
            f = _signatures_for_sketch_factory(args.param_string, 'dna')
            factories.append(f)

        results = []
        for sra in args.sra_accession:
            sigfile = os.path.join(args.output_dir, f'{sra}.{args.sig_extension}')
            name = f'{sra}'
            
            # download SRA file
            fq_files = self.download_sra(sra, args.output_dir, args.threads, verbose=args.verbose)

            # now sketch
            if not args.download_only:
                result = self.sketch_sig(factories, fq_files, name, sigfile, verbose=args.verbose)
                results.append(result)

            # clean up fastq if desired
            for fq_file in fq_files:
                if args.delete_fastq:
                    if args.verbose:
                        notify(f"Removing {fq_file}")
                    os.remove(os.path.join(args.output_dir, fq_file))
        
        if not args.download_only:
            # report on results
            skipped = 0
            total = 0
            for result in results:
                if result is None:
                    skipped += 1
                else:
                    assert result > 0
                    total += result

            notify(f"Produced {total} sketches total for {len(args.sra_accession)} input files.")
            if skipped:
                 notify(f"Skipped {skipped} input files for various reasons.")
