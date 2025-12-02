# Anime Opening Quiz Factory

## Project Overview

Anime Opening Quiz Factory is an automated system designed to create "Guess the Anime Opening/Ending" quiz videos. The system processes anime data from various sources, automatically finds and downloads opening/ending videos, determines optimal timings for quiz segments, assigns difficulty levels, and generates final quiz videos using customizable FFmpeg templates.

## Database Structure

The system uses a PostgreSQL database with the following core tables:

- **animes**: Core table storing anime entries. Each anime has a unique auto-incrementing ID, a Romanian title (`title_ro`), and a status (`status`) which can be NORMAL, FINALIZED (to prevent song list modifications), or BLACKLISTED (to exclude from all processing).
- **id_mappings**: Maps anime entries to external platform IDs. Stores the ID value (`value`) and the platform (`platform`), such as MAL or AniDB, linking back to a specific anime.
- **anime_infos**: A flexible store for additional metadata about an anime, sourced from various external APIs. The `data` field is a JSON object, and each entry is linked to an anime.
- **songs**: Represents individual opening (OP) or ending (ED) songs for an anime. Includes the category, sequence number, song name, and artist. Each song is linked to one anime.
- **sources**: Manages video sources for a song. Stores the source location (e.g., URL, torrent info in a JSON `location` field), the `local_path` after download, and a `status` (NORMAL, INVALID, DOWNLOADING, DOWNLOADED). Each source is linked to one song.
- **timings**: Stores the precise timestamps for a quiz segment derived from a video source. Includes `guess_start` and `reveal_start` times. Each timing entry is linked to one source.
- **levels**: Stores difficulty level assessments for a song. The `value` is an integer from 0 to 100. Each level is linked to one song.
- **worker_results**: Logs the results of automated worker tasks. Tracks the `worker_name`, the target entity (anime, song, or source), and the outcome `status` (SUCCESS, FAIL_INVALID, FAIL_TEMPORARY).

### Database Relationships Schema

```mermaid
erDiagram
    animes {
        int id PK
        str title_ro
        enum status
    }
    id_mappings {
        int id PK
        int anime_id FK
        int value
        enum platform
    }
    anime_infos {
        int id PK
        int anime_id FK
        str source
        json data
    }
    songs {
        int id PK
        int anime_id FK
        enum category
        int number
        str song_artist
        str song_name
    }
    sources {
        int id PK
        int song_id FK
        json location
        str local_path
        enum status
        str added_by
    }
    timings {
        int id PK
        int source_id FK
        float guess_start
        float reveal_start
        str added_by
    }
    levels {
        int id PK
        int song_id FK
        int value
        str added_by
    }
    worker_results {
        int id PK
        str worker_name
        int anime_id FK
        int song_id FK
        int source_id FK
        enum status
    }

    animes ||--o{ id_mappings : "has"
    animes ||--o{ anime_infos : "has"
    animes ||--o{ songs : "has"
    animes ||--o{ worker_results : "target of"
    songs ||--o{ sources : "has"
    songs ||--o{ levels : "has"
    songs ||--o{ worker_results : "target of"
    sources ||--o{ timings : "has"
    sources ||--o{ worker_results : "target of"
```


The database maintains important relationships between these entities through foreign key constraints. Each anime can have multiple songs (openings/endings), and each song can have multiple video sources. Sources can have multiple timing entries, and songs can have multiple difficulty levels from different assessment strategies.

## API Server

The FastAPI server provides RESTful endpoints for managing all database entities. It offers full CRUD operations for animes, songs, sources, timings, and levels. The API handles error cases with appropriate HTTP status codes and provides validation for all input data. The server structure follows a clean separation between routes, models, and service layers.

## Workers System

The project uses a worker-based architecture for automated processing tasks. Workers are independent processes that run concurrently and perform specific operations on the database. Each worker focuses on a single responsibility and uses configurable strategies to handle different scenarios.

Workers are designed to run in parallel with configurable intervals and concurrency settings. They operate by continuously polling the database for new work items, processing them according to their specific strategy, and updating the database with results. This separation allows different types of processing to happen simultaneously without blocking each other.

Key worker categories include source finding workers that search for video sources using different platforms, download workers that handle various download methods, timing workers that analyze videos for optimal quiz segments, and difficulty workers that assign challenge levels. The parallel architecture ensures system scalability and fault isolation.

## Web Interface

The web interface will provide comprehensive management capabilities for the entire system:

- View all data from the database including animes, anime infos, songs, sources, timings, and levels
- "Blocklist" button for anime - prevents any workers from touching the anime or any of its dependent entities, and excludes it from quiz videos
- "Finalize" button for anime - prevents workers from modifying its songs list
- Display download status for song sources showing when a source is currently downloading
- View all running workers with their current status and parameters
- Start new workers with specified parameters like strategy type and execution interval
- Stop existing workers

## Processing Pipeline

The system employs a decentralized processing approach where workers operate independently and in parallel. Unlike traditional sequential pipelines, these workers don't depend on each other's completion. A difficulty level worker can process any song as soon as it exists in the database, without waiting for sources to be found or downloaded. Similarly, source finding workers can search for videos regardless of timing or difficulty processing status.

This architecture allows maximum throughput and resilience. If one type of worker fails or is paused, other workers can continue processing available data. Each worker type focuses on its specific domain while sharing access to the central database, enabling efficient parallel processing across the entire anime catalog without coordination overhead.
