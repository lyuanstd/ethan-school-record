## How to Add New Global Tags

If new Mood or Favourite Activities tags appear frequently, add them to the global lists in `app.py`.

### 1. Update the global list in `routine_data_form()`

For Favourite Activities, find:

```python
common_activities = [
    "Constructive Play",
    "Outdoor Play",
    "Storytime",
    "Music & Movement",
    "Learning Centers",
]
```

Add the new labels, for example:

```python
common_activities = [
    "Constructive Play",
    "Outdoor Play",
    "Storytime",
    "Music & Movement",
    "Learning Centers",
    "Maths & Science",
    "Art & Craft",
    "Indoor Play",
]
```

For Mood, update `common_moods` in the same way.

Note: `accept_new_options=True` is enabled, so one-off new tags can still be added manually without changing the global list.

### 2. Test locally

Run:

```bash
python -m streamlit run app.py
```

Check that the new tags appear correctly in Add/Edit.

### 3. Push the update to GitHub

Check changes:

```bash
git status
```

Stage `app.py`:

```bash
git add app.py
```

Commit:

```bash
git commit -m "Update activity tags"
```

Push:

```bash
git push origin main
```

Streamlit Cloud should automatically redeploy the app after the push.

## Supabase Project
project name: ethan-school-record
database pw: vIvien_y@198633
project URL: https://ktykkdehqtwujpbbeepw.supabase.co