Reverse Engineering Info
========================

This document describes the various APIs and how they work, along with any other
interesting technical tidbits that are useful to know for working on this module.

## Android API

### Updating the Access Token

1. Grab the latest Crunchyroll app APK from the Google Play store using
"com.crunchyroll.crunchyroid" at http://apps.evozi.com/apk-downloader/ (or similar)

2. Decompile the APK at http://www.decompileandroid.com/ (or similar)

3. Retrieve the ACCESS_TOKEN string constant from
src/com/crunchyroll/crunchyroid/Constants.java
