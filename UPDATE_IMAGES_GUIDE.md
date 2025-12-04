# How to Update Movie Images

Follow these steps to fetch fresh poster images for all movies in your dataset.

## Step 1: Get a TMDB API Key

1. Go to [The Movie Database](https://www.themoviedb.org/)
2. Create a free account (or log in if you already have one)
3. Go to Settings → API
4. Request an API key (choose "Developer" option)
5. Fill out the form (you can use "Personal/Educational Project" as the type)
6. Copy your API key

## Step 2: Set the API Key

1. Open the `.env` file in your project root directory
2. Replace `your_api_key_here` with your actual API key:

```
TMDB_API_KEY=abc123def456...
```

3. Save the file

## Step 3: Install Required Package

If you haven't already, install the `python-dotenv` package:

```powershell
pip install python-dotenv
```

## Step 4: Run the Update Script

```powershell
python update_images.py
```

The script will:
- Create a backup of your current dataset (`processed_movies_backup.csv`)
- Search TMDB for each movie by title
- Update image URLs with fresh poster paths
- Show progress as it processes each movie
- Display a summary when complete

**Note:** This will take some time due to API rate limiting (approximately 4 requests per second). For a dataset with 9,000+ movies, expect it to run for about 40-60 minutes.

## Step 5: Restart Your Application

After the script completes, restart your backend server to load the updated dataset:

```powershell
# Stop the current server (Ctrl+C)
# Then restart it:
uvicorn backend.main:app --reload --port 8001
```

## Troubleshooting

**API Key Error:** If you see "TMDB_API_KEY not set in .env file", make sure you:
1. Created the `.env` file in the project root
2. Replaced `your_api_key_here` with your actual API key
3. Saved the file

**Movies Not Found:** Some movies may not be found on TMDB (especially very old or obscure titles). The script will keep the original image URL for these movies.

**Rate Limiting:** If you get rate limit errors, the script will automatically wait between requests. Don't modify the `REQUEST_DELAY` value unless necessary.
