# Deployment Guide for Maintenance Log

## Quick Deploy to Render

### Option 1: Automatic Deployment (Recommended)

1. **Fork this repository** to your GitHub account
2. **Connect to Render**:
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Blueprint"
   - Connect your GitHub account and select this repository
   - Render will automatically detect the `render.yaml` file
3. **Deploy**: Click "Apply" - Render will:
   - Create a PostgreSQL database
   - Deploy the web service
   - Set up environment variables automatically
4. **Access your app**: Use the provided `.onrender.com` URL

### Option 2: Manual Setup

1. **Create Database**:
   - New → PostgreSQL
   - Name: `maintenance-log-db`
   - Plan: Free tier

2. **Create Web Service**:
   - New → Web Service
   - Connect your repository
   - Configure:
     - **Name**: `maintenance-log`
     - **Environment**: Python 3
     - **Build Command**: `pip install -e .`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 main:app`
     - **Instance Type**: Free tier

3. **Environment Variables**:
   - `DATABASE_URL`: Copy from your PostgreSQL database
   - `SESSION_SECRET`: Generate a random 32+ character string

## Environment Variables Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SESSION_SECRET` | Secret key for sessions | `your-random-secret-key-here` |

## Default Login Codes

After deployment, login with these default accounts:
- **Isaak**: `1234`
- **Susie**: `4567`  
- **John**: `7890`

## Post-Deployment Setup

1. **Test the application**: Login with default codes
2. **Add your users**: Go to Users → Add New User
3. **Create categories**: Set up your equipment categories
4. **Add equipment**: Start adding your equipment with photos
5. **Customize**: Update user accounts as needed

## Custom Domain (Optional)

1. In Render dashboard → Settings → Custom Domains
2. Add your domain name
3. Configure DNS CNAME record pointing to your Render URL

## Backup Considerations

- Database backups are handled by Render for paid plans
- Export your data regularly using the built-in PDF export feature
- Consider upgrading to a paid database plan for automated backups

## Scaling

The current configuration supports:
- **Free Tier**: Good for small teams (5-10 users)
- **Starter Plan**: Recommended for production use (unlimited users)
- **Pro Plan**: High availability and performance

## Troubleshooting

### Common Issues

1. **App won't start**: Check environment variables are set correctly
2. **Database connection failed**: Verify DATABASE_URL is correct
3. **Session errors**: Ensure SESSION_SECRET is set and unique
4. **File uploads not working**: Check file permissions and upload directory

### Support

- Check Render logs in dashboard for detailed error messages
- Verify all environment variables are properly set
- Ensure database is running and accessible

## Security Notes

- Never commit secrets to git
- Use strong SESSION_SECRET in production
- Regularly update dependencies
- Consider enabling HTTPS only in production