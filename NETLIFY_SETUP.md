# Netlify Deployment Setup

This repository is configured for automatic deployment to Netlify.

## Build Process

When you push changes to the repository, Netlify will:

1. **Install Python dependencies** from `requirements.txt`
2. **Run the generator**: `python3 tutors-generator/generate-by-dept.py`
   - Generates the module catalogue structure in `tutors-modules-by-dept/`
3. **Run Tutors CLI**: `deno run -A jsr:@tutors/tutors`
   - Converts the Tutors markdown structure to JSON
4. **Deploy**: Publishes the `tutors-generator/tutors-modules-by-dept/json` directory

## Configuration Files

- **`netlify.toml`**: Build and deployment configuration
- **`requirements.txt`**: Python dependencies (PyYAML, python-dotenv)
- **`tutors-generator/.env`**: Environment variables (course ID)

## Environment Variables

The following environment variable is set in `netlify.toml`:

- `TUTORS_COURSE_ID`: `setu-sci-modules` (used in weburl paths)

## Manual Deployment

To test the build process locally:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the generator
cd tutors-generator
python3 generate-by-dept.py

# Run Tutors CLI
deno run -A jsr:@tutors/tutors

# Output will be in tutors-modules-by-dept/json/
```

## Data Sources

The generator uses:
- **Module descriptors**: `Descriptors/yaml/*.yaml`
- **PDFs**: `Descriptors/pdf/*.pdf`
- **Programme registry**: `data/programmes.csv`

## Output Structure

```
tutors-modules-by-dept/
├── unit-1/               # Computing and Mathematics
│   ├── topic-01-programmes/
│   ├── topic-02-clusters/
│   └── topic-03-all-modules/
├── unit-2/               # Science (includes Land Sciences)
│   ├── topic-01-programmes/
│   ├── topic-02-clusters/
│   └── topic-03-all-modules/
└── json/                # Generated JSON for deployment
```

## Troubleshooting

If the build fails:

1. Check the Netlify build logs for errors
2. Verify Python dependencies are correct
3. Ensure all source data files exist (Descriptors, data/programmes.csv)
4. Test the build process locally

## Netlify Dashboard

Configure additional settings in your Netlify dashboard:
- Custom domain
- Deploy previews for pull requests
- Environment variables (if you need to override defaults)
