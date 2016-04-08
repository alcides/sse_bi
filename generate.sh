OUTDIR=analysis_output
mkdir -p $OUTDIR
python coauthors.py > $OUTDIR/coauthors.csv
python coauthors.py year > $OUTDIR/coauthors_by_year.csv
python keywords_histogram.py > $OUTDIR/keywords_histogram.csv
python abstract_histogram.py > $OUTDIR/abstract_histogram.csv
python acm_classification.py > $OUTDIR/acm_classification_by_year.csv