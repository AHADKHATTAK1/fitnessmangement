# 🔧 Use SQLite Locally (Testing Only)

If you want to test the app locally without PostgreSQL:

## Steps:

1. **Remove DATABASE_URL from your local environment:**
   ```bash
   # If you have a .env file, comment out or remove:
   # DATABASE_URL=postgres://...
   ```

2. **Run locally:**
   ```bash
   python app.py
   ```
   
   The app will automatically use SQLite (`gym_manager.db` file)

3. **Access:**
   - Open browser: http://localhost:5000
   - All features will work locally
   - Data stored in `gym_manager.db` file

## ⚠️ Important Notes:

- This is for LOCAL TESTING ONLY
- SQLite data will NOT sync to Render
- For production, you MUST fix the PostgreSQL database on Render
- Once you deploy to Render, it will use PostgreSQL (not SQLite)

## To Go Back to PostgreSQL Locally:

1. Add DATABASE_URL back to `.env` file
2. Point it to a valid PostgreSQL database
3. Restart the app

---

**For production on Render, you MUST follow Option 1 above to create a new PostgreSQL database.**
