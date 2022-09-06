"""Installation script."""
import argparse
import logging
import os
import sys

import pkg_resources as _pkg
import setuptools

import download
# inline:
# from dd import _parser, dddmp
# import git


PACKAGE_NAME = 'dd'
DESCRIPTION = (
    'Binary decision diagrams implemented in pure Python, '
    'as well as Cython wrappers of CUDD, Sylvan, and BuDDy.')
LONG_DESCRIPTION = (
    'dd is a package for working with binary decision diagrams '
    'that includes both a pure Python implementation and '
    'Cython bindings to C libraries (CUDD, Sylvan, BuDDy). '
    'The Python and Cython modules implement the same API, '
    'so the same user code runs with both. '
    'All the standard operations on BDDs are available, '
    'including dynamic variable reordering using sifting, '
    'garbage collection, dump/load from files, plotting, '
    'and a parser of quantified Boolean expressions. '
    'More details can be found in the README at: '
    'https://github.com/tulip-control/dd')
PACKAGE_URL = f'https://github.com/tulip-control/{PACKAGE_NAME}'
PROJECT_URLS = {
    'Bug Tracker':
        'https://github.com/tulip-control/dd/issues',
    'Documentation':
        'https://github.com/tulip-control/dd/blob/main/doc.md',
    'Source Code':
        'https://github.com/tulip-control/dd'}
VERSION_FILE = f'{PACKAGE_NAME}/_version.py'
MAJOR = 0
MINOR = 6
MICRO = 0
VERSION = f'{MAJOR}.{MINOR}.{MICRO}'
VERSION_FILE_TEXT = (
    '# This file was generated from setup.py\n'
    "version = '{version}'\n")
PYTHON_REQUIRES = '>=3.11'
install_requires = [
    'astutils >= 0.0.5',
    'networkx >= 2.4',
    'ply >= 3.4, <= 3.10',
    'pydot >= 1.2.2',
    'setuptools >= 65.6.0']
TESTS_REQUIRE = [
    'pytest >= 4.6.11']
CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Cython',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development']
KEYWORDS = [
    'bdd',
    'binary decision diagram',
    'decision diagram',
    'boolean',
    'networkx',
    'dot',
    'graphviz']


def git_version(version):
    """Return version with local version identifier."""
    import git as _git
    repo = _git.Repo('.git')
    repo.git.status()
    # assert versions are increasing
    latest_tag = repo.git.describe(
        match='v[0-9]*', tags=True, abbrev=0)
    latest_version = _pkg.parse_version(latest_tag)
    given_version = _pkg.parse_version(version)
    if latest_version > given_version:
        raise AssertionError(
            (latest_tag, version))
    sha = repo.head.commit.hexsha
    if repo.is_dirty():
        return f'{version}.dev0+{sha}.dirty'
    # commit is clean
    # is it release of `version` ?
    try:
        tag = repo.git.describe(
            match='v[0-9]*', exact_match=True,
            tags=True, dirty=True)
    except _git.GitCommandError:
        return f'{version}.dev0+{sha}'
    if tag != f'v{version}':
        raise AssertionError((tag, version))
    return version


def parse_args():
    """Return `args` irrelevant to `setuptools`."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--fetch', action='store_true',
        help='download cudd from its website')
    parser.add_argument(
        '--linetrace', action='store_true',
        help='use line tracing for Cython extensions')
    for opt in download.EXTENSIONS:
        parser.add_argument(
            f'--{opt}', default=None,
            const='', type=str, nargs='?',
            help=f'build Cython extension {opt}')
    args, unknown = parser.parse_known_args()
    args.sdist = 'sdist' in unknown
    args.bdist_wheel = 'bdist_wheel' in unknown
    # avoid confusing `setuptools`
    sys.argv = [sys.argv[0], *unknown]
    return args


def read_env_vars(
        ) -> dict:
    """Read relevant environment variables."""
    keys = {
        k: ''
        for k in download.EXTENSIONS}
    keys['fetch'] = True
    env_vars = {
        k: v
        for k, v in keys.items()
        if f'DD_{k.upper()}' in os.environ}
    print('`setup.py` of `dd` read environment variables:')
    print(env_vars)
    return env_vars


def run_setup():
    """Build parser, get version from `git`, install."""
    env_vars = read_env_vars()
    args = parse_args()
    dargs = vars(args)
    for k, v in env_vars.items():
        if dargs[k] in (None, False):
            dargs[k] = v
    if args.fetch:
        download.fetch_cudd()
    # build extensions ?
    ext_modules = download.extensions(args)
    # version
    try:
        version = git_version(VERSION)
    except AssertionError:
        raise
    except:
        print('No git info: Assume release.')
        version = VERSION
    s = VERSION_FILE_TEXT.format(version=version)
    with open(VERSION_FILE, 'w') as f:
        f.write(s)
    _build_parsers()
    setuptools.setup(
        name=PACKAGE_NAME,
        version=version,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author='Caltech Control and Dynamical Systems',
        author_email='tulip@tulip-control.org',
        url=PACKAGE_URL,
        project_urls=PROJECT_URLS,
        license='BSD',
        python_requires=PYTHON_REQUIRES,
        install_requires=install_requires,
        tests_require=TESTS_REQUIRE,
        packages=[PACKAGE_NAME],
        package_dir={PACKAGE_NAME: PACKAGE_NAME},
        include_package_data=True,
        ext_modules=ext_modules,
        classifiers=CLASSIFIERS,
        keywords=KEYWORDS)


def _build_parsers(
        ) -> None:
    """Cache each parser's state machine."""
    if not _parser_requirements_installed():
        return
    import dd.dddmp
    import dd._parser
    logging.getLogger('astutils').setLevel('ERROR')
    dd.dddmp._rewrite_tables(outputdir=PACKAGE_NAME)
    dd._parser._rewrite_tables(outputdir=PACKAGE_NAME)


def _parser_requirements_installed(
        ) -> bool:
    """Return `True` if parser requirements found."""
    try:
        import astutils
        import ply
    except ImportError:
        print(
            'WARNING: `dd` could not cache parser tables '
            '(ignore this if running only for metadata information).')
        return False
    return True


if __name__ == '__main__':
    run_setup()
