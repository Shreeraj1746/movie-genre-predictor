# Movie Data

This directory contains the movie dataset files.

## Data Sources

For this project, we use the [CMU Movie Summary Corpus](http://www.cs.cmu.edu/~ark/personas/). This dataset contains:

- Plot summaries for 42,306 movies extracted from Wikipedia
- Movie metadata (including genre) for 81,741 movies extracted from Freebase

## Data Structure

After downloading and preprocessing, the data will be organized as follows:

```
data/
├── raw/
│   ├── movie.metadata.tsv          # Original metadata file
│   └── plot_summaries.txt          # Original plot summaries file
└── processed/
    ├── movies_with_plots.csv       # Merged and cleaned dataset
    ├── train.csv                   # Training dataset
    ├── test.csv                    # Test dataset
    └── validation.csv              # Validation dataset
```

## Data Fields

The processed dataset (`movies_with_plots.csv`) contains the following fields:

- `movie_id`: Unique identifier for the movie
- `title`: Movie title
- `plot`: Plot summary text
- `genre`: Primary genre (target variable)
- `release_year`: Year the movie was released
- `runtime`: Movie runtime in minutes

## License

The CMU Movie Summary Corpus is released under a Creative Commons Attribution-ShareAlike 3.0 Unported License (CC BY-SA 3.0).
