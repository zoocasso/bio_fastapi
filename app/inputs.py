"""Reading a person's genotypes into the rows the annotation pipeline joins on.

Two inputs are supported: a single-sample VCF, and the tab-separated raw export of a genotyping
chip (rsID, chromosome, position, genotype; lines starting with # are comments).

Chromosome names and alleles are normalized here, so the SQL stages compare them exactly: the
reference tables name chromosomes 1-22, X, Y and MT (GRCh37) and write alleles in upper case.
"""

import logging
import re
from pathlib import Path

import pandas as pd
import vcf

log = logging.getLogger(__name__)

SAMPLE_FIELDS = ("GT", "AD", "DP", "GQ", "PL")
# "chrM" in hg19-style files; 23-26 are the chip (PLINK) codes for X, Y, the X/Y pseudo-autosomal
# region (on X in GRCh37 coordinates) and MT
_CHROM_ALIASES = {"M": "MT", "XY": "X", "23": "X", "24": "Y", "25": "X", "26": "MT"}


def normalize_chrom(name: str) -> str:
    """ "chr1" -> "1", "chrX" or "x" -> "X", "chrM" -> "MT", chip "23" -> "X"."""
    chrom = str(name).strip().upper().removeprefix("CHR")
    return _CHROM_ALIASES.get(chrom, chrom)


def _alleles(genotype: str) -> tuple[str, str]:
    """ "A/G" or "A|G" -> ("A", "G"); a haploid call such as "A" counts as homozygous."""
    parts = re.split(r"[/|]", genotype)
    return (parts[0], parts[0]) if len(parts) == 1 else (parts[0], parts[1])


def read_vcf(path: Path) -> pd.DataFrame:
    rows, skipped = [], 0
    with open(path) as f:
        for record in vcf.Reader(f):
            call = record.samples[0]
            if not call.called or call.gt_bases is None:
                skipped += 1
                continue
            allele_1, allele_2 = (a.upper() for a in _alleles(call.gt_bases))
            chrom, ref = normalize_chrom(record.CHROM), record.REF.upper()
            # the ALT the person carries, so a 0/2 call is keyed by the second ALT; a call without
            # one (0/0, 0/.) keeps the first, and the GWAS stage then finds its copies unknown
            alt = next((a for a in (allele_1, allele_2) if a not in (ref, ".")), str(record.ALT[0]).upper())
            data = call.data
            rows.append(
                {
                    "chrom": chrom,
                    "pos": int(record.POS),
                    "id": str(record.ID),
                    "ref": ref,
                    "alt": alt,
                    "qual": str(record.QUAL),
                    # PyVCF reads "PASS" as [] and "." (filters not applied) as None
                    "filter": "." if record.FILTER is None else ";".join(record.FILTER) or "PASS",
                    "info": str(record.INFO),
                    "format": str(record.FORMAT),
                    "sample_data": ";".join(
                        str(getattr(data, f)) for f in SAMPLE_FIELDS if getattr(data, f, None) is not None
                    ),
                    "allele_1": allele_1,
                    "allele_2": allele_2,
                    # the key every reference table is joined on
                    "connect_key": f"{chrom}-{record.POS}-{ref}-{alt}",
                }
            )
    if skipped:
        log.info("%s: skipped %d records without a called genotype", path.name, skipped)
    return pd.DataFrame(rows)


def read_array(path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep="\t",
        comment="#",
        names=["rsID", "CHR", "POS", "genotype"],
        dtype={"rsID": str, "CHR": str, "POS": int, "genotype": str},
    )
    df["CHR"] = df["CHR"].map(normalize_chrom)
    # "--" is a no-call on most chips; it stays in so the row count matches the export, and the GWAS
    # stage finds its copies unknown
    genotypes = df["genotype"].fillna("--").str.strip().str.upper()
    alleles = genotypes.map(lambda g: (g[0], g[0]) if len(g) == 1 else (g[0], g[1]))
    df["allele_1"] = alleles.str[0]
    df["allele_2"] = alleles.str[1]
    return df[["CHR", "POS", "rsID", "allele_1", "allele_2"]]
