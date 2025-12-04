import pandas as pd
import requests
import time
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# TMDB API Configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
TMDB_SEARCH_URL = 'https://api.themoviedb.org/3/search/movie'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

# Rate limiting: TMDB allows 40 requests per 10 seconds
REQUEST_DELAY = 0.26  # ~3.8 requests per second to be safe

def search_movie_poster(title: str, year: Optional[str] = None) -> Optional[str]:
    """
    Search for a movie by title and return the poster path.
    
    Args:
        title: Movie title to search for
        year: Optional release year to improve search accuracy
        
    Returns:
        Poster path if found, None otherwise
    """
    try:
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'language': 'en-US',
            'page': 1
        }
        
        if year:
            params['year'] = year
        
        response = requests.get(TMDB_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        
        if results:
            # Get the first result (most relevant)
            poster_path = results[0].get('poster_path')
            if poster_path:
                return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
        
        return None
        
    except Exception as e:
        print(f"Error searching for '{title}': {e}")
        return None

def update_movie_images(input_csv: str, output_csv: str, backup: bool = True):
    """
    Update movie images in the dataset by fetching fresh URLs from TMDB.
    
    Args:
        input_csv: Path to input CSV file
        output_csv: Path to output CSV file
        backup: Whether to create a backup of the original file
    """
    print(f"Loading dataset from {input_csv}...")
    df = pd.read_csv(input_csv)
    
    if backup:
        backup_path = input_csv.replace('.csv', '_backup.csv')
        df.to_csv(backup_path, index=False)
        print(f"Backup created at {backup_path}")
    
    total_movies = len(df)
    updated_count = 0
    failed_count = 0
    
    print(f"\nProcessing {total_movies} movies...")
    print("This may take a while due to API rate limiting.\n")
    
    for idx, row in df.iterrows():
        title = row['title']
        current_url = row.get('image_url', '')
        
        # Extract year from release_date if available
        year = None
        if 'release_date' in df.columns and pd.notna(row['release_date']):
            try:
                year = str(row['release_date'])[:4]
            except:
                pass
        
        print(f"[{idx + 1}/{total_movies}] Searching for: {title}", end='')
        
        # Search for the movie poster
        new_url = search_movie_poster(title, year)
        
        if new_url:
            df.at[idx, 'image_url'] = new_url
            updated_count += 1
            print(f" ✓ Updated")
        else:
            failed_count += 1
            print(f" ✗ Not found (keeping original)")
        
        # Rate limiting
        time.sleep(REQUEST_DELAY)
        
        # Progress update every 50 movies
        if (idx + 1) % 50 == 0:
            print(f"\nProgress: {idx + 1}/{total_movies} | Updated: {updated_count} | Failed: {failed_count}\n")
    
    # Save updated dataset
    print(f"\nSaving updated dataset to {output_csv}...")
    df.to_csv(output_csv, index=False)
    
    print("\n" + "="*60)
    print("UPDATE COMPLETE")
    print("="*60)
    print(f"Total movies: {total_movies}")
    print(f"Successfully updated: {updated_count}")
    print(f"Failed to find: {failed_count}")
    print(f"Success rate: {(updated_count/total_movies)*100:.1f}%")
    print("="*60)

def main():
    """Main function to run the image update process."""
    
    # Check for API key
    if not TMDB_API_KEY or TMDB_API_KEY == 'your_api_key_here':
        print("ERROR: TMDB_API_KEY not set in .env file!")
        print("\nTo set it:")
        print("1. Open the .env file in your project root")
        print("2. Replace 'your_api_key_here' with your actual API key")
        print("3. Save the file")
        print("\nGet your free API key at: https://www.themoviedb.org/settings/api")
        return
    
    input_file = 'data/processed_movies.csv'
    output_file = 'data/processed_movies.csv'
    
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        return
    
    print("="*60)
    print("TMDB Movie Image Updater")
    print("="*60)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"API Key: {TMDB_API_KEY[:8]}..." if len(TMDB_API_KEY) > 8 else "Set")
    print("="*60)
    
    # Confirm before proceeding
    response = input("\nProceed with update? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Update cancelled.")
        return
    
    update_movie_images(input_file, output_file)

if __name__ == "__main__":
    main()
