# Netlify Deployment Setup

This repository is configured for automatic deployment to Netlify.

## Build Process

When you push changes to the repository, Netlify will:

1. **Install Python dependencies** from `requirements.txt`
2. **Run the generator**: `cd tutors-generator && python3 generate-by-dept.py`
   - Generates the module catalogue structure in `tutors-modules-by-dept/` (at repo root)
3. **Run Tutors CLI**: `cd tutors-modules-by-dept && deno run -A jsr:@tutors/tutors`
   - Converts the Tutors markdown structure to JSON
4. **Deploy**: Publishes the `tutors-modules-by-dept/json` directory

## Repository Structure

```
setu-catalogues/live/
├── tutors-generator/           # Generator scripts
│   ├── generate-by-dept.py     # Main generator script
│   ├── cluster-icons.yaml      # Icon mappings
│   ├── programme-icons.yaml    # Programme icons
│   └── .env                    # Environment variables (not in Git)
├── tutors-modules-by-dept/     # Generated course (at root)
│   ├── unit-1/                 # Computing and Mathematics
│   ├── unit-2/                 # Science (includes Land Sciences)
│   └── json/                   # Generated JSON for deployment
├── Descriptors/                # Source data
│   ├── yaml/                   # Module descriptors
│   └── pdf/                    # Module PDFs
├── data/
│   └── programmes.csv          # Programme registry
├── netlify.toml                # Netlify configuration
└── requirements.txt            # Python dependencies
```

## Configuration Files

- **`netlify.toml`**: Build and deployment configuration
- **`requirements.txt`**: Python dependencies (PyYAML, python-dotenv)
- **`tutors-generator/.env`**: Environment variables (course ID, not in Git)

## Environment Variables

The following environment variable is set in `netlify.toml`:

- `TUTORS_COURSE_ID`: `setu-sci-modules` (used in weburl paths)

## Manual Deployment

To test the build process locally:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the generator (from tutors-generator directory)
cd tutors-generator
python3 generate-by-dept.py

# Run Tutors CLI (from generated course directory)
cd ../tutors-modules-by-dept
deno run -A jsr:@tutors/tutors

# Output will be in tutors-modules-by-dept/json/
```

## Data Sources

The generator uses:
- **Module descriptors**: `Descriptors/yaml/*.yaml`
- **PDFs**: `Descriptors/pdf/*.pdf`
- **Programme registry**: `data/programmes.csv`
- **Icon mappings**: `tutors-generator/cluster-icons.yaml`, `programme-icons.yaml`

## Output Structure

```
tutors-modules-by-dept/
├── course.md             # Course overview
├── course.png            # Course image
├── properties.yaml       # Course properties
├── unit-1/               # Computing and Mathematics Department
│   ├── topic-01-programmes/     # 15 programmes
│   ├── topic-02-clusters/       # 14 subject clusters
│   └── topic-03-all-modules/    # 238 modules alphabetically
├── unit-2/               # Science Department (includes Land Sciences)
│   ├── topic-01-programmes/     # 20 programmes (9 Science + 11 Land Sciences)
│   ├── topic-02-clusters/       # 15 subject clusters
│   └── topic-03-all-modules/    # 280 modules alphabetically
└── json/                # Generated JSON for deployment
    ├── index.html
    ├── tutors.json
    └── [additional JSON files]
```

## Troubleshooting

If the build fails:

1. Check the Netlify build logs for errors
2. Verify Python dependencies are correct
3. Ensure all source data files exist (Descriptors, data/programmes.csv)
4. Test the build process locally
5. Verify the Tutors CLI runs from the `tutors-modules-by-dept` directory

## Netlify Dashboard

Configure additional settings in your Netlify dashboard:
- Custom domain
- Deploy previews for pull requests
- Environment variables (if you need to override defaults)
- Build & deploy settings (should auto-detect from netlify.toml)
