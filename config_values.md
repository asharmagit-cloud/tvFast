# Configuration Values

## Environment Variables

Create a `.env` file in the root directory with the following values:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DB_NAME=fasttv_db

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Default Values (if .env is not provided)

The application will use these default values if environment variables are not set:

- **MONGODB_URL**: `mongodb://localhost:27017`
- **DB_NAME**: `fasttv_db`
- **SECRET_KEY**: `your-super-secret-key-change-this-in-production-12345`
- **ALGORITHM**: `HS256`
- **ACCESS_TOKEN_EXPIRE_MINUTES**: `30`

## Production Recommendations

For production deployment, make sure to:

1. **Change the SECRET_KEY** to a strong, random string (at least 32 characters)
2. **Use MongoDB Atlas** or a secure MongoDB instance
3. **Set proper CORS origins** in main.py
4. **Use environment variables** instead of hardcoded values
5. **Enable MongoDB authentication** if needed

## MongoDB Atlas Example

If using MongoDB Atlas, your MONGODB_URL would look like:
```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
```

## Security Notes

- Never commit the `.env` file to version control
- Use strong, unique secret keys in production
- Consider using a secrets management service for production
- Regularly rotate your secret keys
