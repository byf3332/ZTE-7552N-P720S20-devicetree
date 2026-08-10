#
# Legacy compatibility. AndroidProducts.mk is the authoritative lunch list.
add_lunch_combo twrp_P720S20-eng

# TeamWin 12.1's minuitwrp DRM backend assumes Qualcomm SDE atomic
# mode_properties and two layer mixers. P720S20 uses Unisoc sprd-drm and has
# no fbdev fallback, so install TeamWin's generic KMS backend before Soong
# compiles libminuitwrp.
_p720s20_tree_dir="$(
    cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd
)"
_p720s20_android_top="${ANDROID_BUILD_TOP:-}"
if [[ -z "${_p720s20_android_top}" ]] && declare -F gettop >/dev/null 2>&1; then
    _p720s20_android_top="$(gettop)"
fi
if [[ -z "${_p720s20_android_top}" ]]; then
    echo "P720S20: unable to locate Android build root" >&2
    return 1
fi
python3 "${_p720s20_tree_dir}/tools/install_generic_drm_backend.py" \
    "${_p720s20_tree_dir}/patches/graphics_drm.cpp" \
    "${_p720s20_android_top}/bootable/recovery/minuitwrp/graphics_drm.cpp" || return 1
python3 "${_p720s20_tree_dir}/tools/install_p720s20_reboot_bcb.py" \
    "${_p720s20_android_top}/bootable/recovery/twrp-functions.cpp" || return 1
python3 "${_p720s20_tree_dir}/tools/install_p720s20_battery_status.py" \
    "${_p720s20_android_top}/bootable/recovery/twrp.cpp" || return 1
python3 "${_p720s20_tree_dir}/tools/install_p720s20_keystore2_fix.py" \
    "${_p720s20_android_top}/system/vold/Keymaster.cpp" \
    "${_p720s20_android_top}/system/vold/Keymaster.h" \
    "${_p720s20_android_top}/system/vold/KeyStorage.cpp" \
    "${_p720s20_android_top}/system/vold/MetadataCrypt.cpp" \
    "${_p720s20_android_top}/system/vold/KeyUtil.cpp" || return 1
python3 "${_p720s20_tree_dir}/tools/install_p720s20_metadata_fbe_remount.py" \
    "${_p720s20_android_top}/bootable/recovery/partitionmanager.cpp" || return 1
python3 "${_p720s20_tree_dir}/tools/install_p720s20_adb_reboot.py" \
    "${_p720s20_android_top}/system/core/reboot/reboot.c" || return 1
unset _p720s20_android_top _p720s20_tree_dir
