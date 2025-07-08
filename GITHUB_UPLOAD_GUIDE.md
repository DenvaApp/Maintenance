# Files to Upload to GitHub for Render Deployment

## Critical Issue: Database Persistence Fixed

The main issue was that Render uses PostgreSQL URLs starting with `postgres://` but SQLAlchemy 2.0+ requires `postgresql://`. This has been fixed in the updated `app.py` file.

## Files You Need to Upload/Update on GitHub:

### 1. Updated Core Files (Replace existing files)
- `app.py` - Fixed PostgreSQL URL format
- `render.yaml` - Updated build command  
- `build.sh` - Build script (already exists)

### 2. Missing Icons Folder (CREATE THIS FOLDER)
Create `static/icons/` folder and upload these SVG files:
- `pepper-shoots.svg`
- `pepper-bin.svg`
- `tow-buggy.svg`
- `spray-robot.svg`
- `spray-wagon.svg`
- `motor.svg`
- `forklift.svg`
- `scissor-lift.svg`
- `greenhouse-fan.svg`
- `heating-system.svg`
- `irrigation-system.svg`

### 3. After Upload:
1. Render will automatically redeploy
2. The database should now properly persist data
3. Your custom icons will appear in the equipment forms

## The Fix:
The PostgreSQL URL format issue was preventing proper database connections on Render, causing data to be lost between sessions. This is now resolved.