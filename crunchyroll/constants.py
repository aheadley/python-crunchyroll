CR_ACCESS_TOKEN         = '1M8BbXptBS4VhMP'
CR_API_ENDPOINT         = 'api.crunchyroll.com'
CR_API_URL              = '{protocol}://' + CR_API_ENDPOINT + '/' \
                            '{api_method}.{version}.json'
# this is probably dumb but whatever
CR_API_SECURE_PROTO     = 'https'
CR_API_INSECURE_PROTO   = 'http'

# not used yet
CR_PREMIUM_TYPE_ANIME   = '2'
CR_PREMIUM_TYPE_DRAMA   = '4'

# media type flags
CR_MEDIA_TYPE_ANIME     = 'anime'
CR_MEDIA_TYPE_DRAMA     = 'drama'

CR_PREMIUM_FLAG_ANIME       = 'anime'
CR_PREMIUM_FLAG_DRAMA       = 'drama'
CR_PREMIUM_FLAG_TAISENG     = 'taiseng'
# filter flags
CR_FILTER_POPULAR           = 'popular'
CR_FILTER_SIMULCAST         = 'simulcast'
CR_FILTER_UPDATED           = 'updated'
CR_FILTER_ALPHA             = 'alpha'
CR_FILTER_NEWEST            = 'newest'
CR_FILTER_PREFIX            = 'prefix:'
CR_FILTER_TAG               = 'tag:'

# these are apparently like database fields or something that you can add
# to the list_series, list_media, and info methods to get additional or only
# specific info. of particular note is the CR_FIELD_MEDIA_STREAM_DATA field
# to get the streams
CR_FIELD_GENERAL_MOST_LIKELY_MEDIA  = 'most_likely_media'
CR_FIELD_GENERAL_ORDERING           = 'ordering'
CR_FIELD_MEDIA_ID                   = 'media.media_id'
CR_FIELD_MEDIA_NAME                 = 'media.name'
CR_FIELD_MEDIA_EPISODE_NUMBER       = 'media.episode_number'
CR_FIELD_MEDIA_SCREENSHOT_IMAGE     = 'media.screenshot_image'
CR_FIELD_MEDIA_STREAM_DATA          = 'media.stream_data'
CR_FIELD_MEDIA_FREE_AVAILABLE       = 'media.free_available'
CR_FIELD_MEDIA_PREMIUM_AVAILABLE    = 'media.premium_available'
CR_FIELD_MEDIA_AVAILABILITY_NOTES   = 'media.availablity_notes'
CR_FIELD_MEDIA_PLAYHEAD             = 'media.playhead'
CR_FIELD_MEDIA_TYPE                 = 'media.media_type'
CR_FIELD_MEDIA_DESCRIPTION          = 'media.description'
CR_FIELD_SERIES                     = 'series'
CR_FIELD_SERIES_ID                  = 'series.series_id'
CR_FIELD_SERIES_NAME                = 'series.name'
CR_FIELD_SERIES_PUBLISHER_NAME      = 'series.publisher_name'
CR_FIELD_SERIES_YEAR                = 'series.year'
CR_FIELD_SERIES_SCREENSHOT_IMAGE    = 'series.screenshot_image'
CR_FIELD_SERIES_LANDSCAPE_IMAGE     = 'series.landscape_image'
CR_FIELD_SERIES_PORTRAIT_IMAGE      = 'series.portrait_image'
CR_FIELD_SERIES_MEDIA_COUNT         = 'series.media_count'
CR_FIELD_SERIES_MEDIA_TYPE          = 'series.media_type'
CR_FIELD_SERIES_IN_QUEUE            = 'series.in_queue'
CR_FIELD_SERIES_DESCRIPTION         = 'series.description'
CR_FIELD_IMAGE_FWIDE_URL            = 'image.fwide_url'
CR_FIELD_IMAGE_WIDESTAR_URL         = 'image.widestar_url'
CR_FIELD_IMAGE_LARGE_URL            = 'image.large_url'
CR_FIELD_IMAGE_FULL_URL             = 'image.full_url'

ANDROID_DEVICE_MANUFACTURER = 'unknown'
ANDROID_DEVICE_MODEL        = 'google_sdk'
ANDROID_DEVICE_PRODUCT      = 'google_sdk'
# this should probably be replaced with a random UUIDv4 in api init
ANDROID_DEVICE_ID           = '00000000-18c4-ade8-ffff-ffff99d603a9'
ANDROID_SDK_VERSION         = '17'
ANDROID_RELEASE_VERSION     = '4.2'
ANDROID_APP_CODE            = '66'
ANDROID_APP_VERSION_NAME    = '0.7.9'
ANDROID_APP_PACKAGE         = 'com.crunchyroll.crunchyroid'
ANDROID_USER_AGENT          = 'Dalvik/1.6.0 (Linux; U; Android 4.2; google_sdk Build/JB_MR1)'

