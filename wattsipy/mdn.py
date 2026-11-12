"""MDN annotations handler for WattsiPy."""

from __future__ import annotations
from typing import Optional, Union

from .dom import (
    Element,
    Node,
    E,
    T,
    NS_HTML,
    PROP_HEADING,
    has_ancestor,
    has_ancestor_with_properties,
)

MDN_BROWSERS = {
    "chrome": "Chrome",
    "chrome_android": "Chrome Android",
    "edge_blink": "Edge",
    "edge": "Edge (Legacy)",
    "firefox": "Firefox",
    "firefox_android": "Firefox Android",
    "ie": "Internet Explorer",
    "opera": "Opera",
    "opera_android": "Opera Android",
    "safari": "Safari",
    "safari_ios": "Safari iOS",
    "samsunginternet_android": "Samsung Internet",
    "webview_android": "WebView Android",
}

BROWSERS_PROVIDING_CURRENT_ENGINES = ["firefox", "safari", "chrome"]
BROWSERS_WITH_BORROWED_ENGINES = ["opera", "edge_blink"]
BROWSERS_WITH_RETIRED_ENGINES = ["edge", "ie"]
BROWSERS_FOR_MOBILE_DEVICES = [
    "firefox_android",
    "safari_ios",
    "chrome_android",
    "webview_android",
    "samsunginternet_android",
    "opera_android",
]

MDN_URL_BASE = "https://developer.mozilla.org/en-US/docs/Web/"
CAN_I_USE_URL_BASE = "https://caniuse.com/#feat="
CAN_I_USE_TEXT = "caniuse.com table"
FLAG_CLASS_LESS_THAN_TWO = "less-than-two-engines-flag"
FLAG_CLASS_ALL = "all-engines-flag"
ENGINES_CLASS_LESS_THAN_TWO = "less-than-two-engines-text"
ENGINES_CLASS_ALL = "all-engines-text"
IN_NONE = "No support in current engines."
IN_ONE = "Support in one engine only."
IN_ALL = "Support in all current engines."
ALT_NAME_IN_ONE = "Support in one engine under other name."
ALT_NAME_IN_SOME = "Support in some engines under other name."
PREFIX_IN_ONE = "Prefixed support in one engine."
PREFIX_IN_SOME = "Prefixed support in some engines."
PARTIAL_IN_ONE = "Partial support in one engine."
PARTIAL_IN_SOME = "Partial support in some engines."


def add_mdn_browser_row(
    support_table: Element,
    browser_id: str,
    yes_no_unknown: str,
    version: str,
    is_partial: bool,
    needs_flag: bool,
    needs_prefix_or_alt_name: bool,
) -> None:
    browser_class = f"{browser_id} {yes_no_unknown}"
    flag_symbol = ""
    browser_version_attributes: dict[str, str] = {"data-x": ""}
    if is_partial or needs_flag or needs_prefix_or_alt_name:
        flag_symbol = "\U0001f530 "  # 🔰
    if needs_prefix_or_alt_name:
        browser_version_attributes = {
            "data-x": "",
            "title": "Requires a prefix or alternative name.",
        }
    if needs_flag:
        browser_version_attributes = {
            "data-x": "",
            "title": "Requires setting a user preference or runtime flag.",
        }
    if is_partial:
        browser_version_attributes = {
            "data-x": "",
            "title": "Partial implementation.",
        }
    if browser_id == "edge_blink":
        browser_class = f"edge_blink {yes_no_unknown}"
    elif browser_id == "edge":
        browser_class = f"edge {yes_no_unknown}"

    browser_row = E("span", ["data-x", "", "class", browser_class])
    browser_row.append_child(E("span", ["data-x", ""], [T(MDN_BROWSERS[browser_id])]))
    browser_row.append_child(E("span", browser_version_attributes, [T(flag_symbol + version)]))
    support_table.append_child(browser_row)


def get_version_as_string(version) -> str:
    if version is None:
        return ""
    if isinstance(version, bool):
        return "True" if version else "False"
    return str(version)


def get_version_or_range(
    browser_id: str,
    version_added: str,
    version_removed: str,
    yes_no_unknown: str,
) -> str:
    if yes_no_unknown == "unknown":
        return "?"
    if version_added == "False":
        return "No"
    if not version_removed or version_removed == "False":
        if yes_no_unknown == "no":
            return "No"
        if version_added == "True":
            return "Yes"
        if browser_id == "edge" and version_added == "18":
            return "18"
        if browser_id == "ie" and version_added == "11":
            return "11"
        return version_added + "+"
    if not version_added:
        return "No"
    if version_removed == "True" or version_added == "True":
        return "No"
    return f"{version_added}\u2013{version_removed}"  # en-dash \u2013


def process_browser_data(browser_id: str, version_data, support_table: Element) -> None:
    needs_flag = False
    needs_prefix_or_alt_name = False
    is_partial = False
    yes_no_unknown = "unknown"
    version_added = ""
    version_removed = ""

    if isinstance(version_data, list):
        for version_details in version_data:
            needs_flag = False
            version_added = get_version_as_string(version_details.get("version_added"))
            version_removed = get_version_as_string(version_details.get("version_removed"))
            if version_removed and version_removed != "False":
                yes_no_unknown = "no"
                continue
            if version_added:
                yes_no_unknown = "no" if version_added == "False" else "yes"
                if "partial_implementation" in version_details:
                    is_partial = True
                if "flags" in version_details:
                    needs_flag = True
                if "prefix" in version_details or "alternative_name" in version_details:
                    needs_prefix_or_alt_name = True
                if not needs_flag and not is_partial and not needs_prefix_or_alt_name:
                    break
                if is_partial:
                    break
                if needs_flag:
                    break
    elif isinstance(version_data, dict):
        version_added = get_version_as_string(version_data.get("version_added"))
        version_removed = get_version_as_string(version_data.get("version_removed"))
        if version_removed and version_removed != "False":
            yes_no_unknown = "no"
        else:
            if version_added:
                yes_no_unknown = "no" if version_added == "False" else "yes"
                if "partial_implementation" in version_data:
                    is_partial = True
                if "flags" in version_data:
                    needs_flag = True
                if "prefix" in version_data or "alternative_name" in version_data:
                    needs_prefix_or_alt_name = True

    version = get_version_or_range(browser_id, version_added, version_removed, yes_no_unknown)
    add_mdn_browser_row(
        support_table,
        browser_id,
        yes_no_unknown,
        version,
        is_partial,
        needs_flag,
        needs_prefix_or_alt_name,
    )


def add_mdn_box(mdn_box: Element, elem_id: str, mdn_json_data: dict, is_first: bool) -> None:
    items = mdn_json_data.get(elem_id)
    if not isinstance(items, list):
        return

    for mdn_data in items:
        mdn_slug = mdn_data.get("slug", "")
        mdn_summary = mdn_data.get("summary", "")
        slash_pos = mdn_slug.find("/")
        mdn_subpath = mdn_slug[slash_pos + 1:] if slash_pos != -1 else mdn_slug
        mdn_support = mdn_data.get("support")
        engines = mdn_data.get("engines")
        engine_count = len(engines) if isinstance(engines, list) else -1

        if is_first:
            mdn_button = E("button", ["class", "mdn-anno-btn", "onclick", "toggleStatus(this)"])
            flag_class_name = ""
            flag_symbol = ""
            flag_title = ""
            if engine_count == 0:
                flag_class_name = FLAG_CLASS_LESS_THAN_TWO
                flag_symbol = "\u26A0"  # ⚠
                flag_title = IN_NONE
                if "altname" in mdn_data:
                    flag_title = ALT_NAME_IN_SOME if len(mdn_data["altname"]) > 1 else ALT_NAME_IN_ONE
                elif "prefixed" in mdn_data:
                    flag_title = PREFIX_IN_SOME if len(mdn_data["prefixed"]) > 1 else PREFIX_IN_ONE
                elif "partial" in mdn_data:
                    flag_title = PARTIAL_IN_SOME if len(mdn_data["partial"]) > 1 else PARTIAL_IN_ONE
            elif engine_count == 1:
                flag_class_name = FLAG_CLASS_LESS_THAN_TWO
                flag_symbol = "\u26A0"
                flag_title = IN_ONE
            elif engine_count >= len(BROWSERS_PROVIDING_CURRENT_ENGINES):
                flag_class_name = FLAG_CLASS_ALL
                flag_symbol = "\u2714"  # ✔
                flag_title = IN_ALL

            if engine_count != 2 and mdn_support is not None:
                mdn_button.append_child(E("b", ["class", flag_class_name, "title", flag_title], [T(flag_symbol)]))
            mdn_button.append_child(E("span", ["data-x", ""], [T("MDN")]))
            mdn_box.append_child(mdn_button)
        is_first = False

        mdn_feature = E("div", ["class", "feature"])
        mdn_feature.append_child(E("p", [
            E("a", ["href", MDN_URL_BASE + mdn_slug, "title", mdn_summary], [T(mdn_subpath)])
        ]))
        mdn_box.append_child(mdn_feature)

        engines_class_name = ""
        engines_text = ""
        if engine_count == 0:
            engines_class_name = ENGINES_CLASS_LESS_THAN_TWO
            engines_text = IN_NONE
            if "altname" in mdn_data:
                engines_text = ALT_NAME_IN_SOME if len(mdn_data["altname"]) > 1 else ALT_NAME_IN_ONE
            elif "prefixed" in mdn_data:
                engines_text = PREFIX_IN_SOME if len(mdn_data["prefixed"]) > 1 else PREFIX_IN_ONE
            elif "partial" in mdn_data:
                engines_text = PARTIAL_IN_SOME if len(mdn_data["partial"]) > 1 else PARTIAL_IN_ONE
        elif engine_count == 1:
            engines_class_name = ENGINES_CLASS_LESS_THAN_TWO
            engines_text = IN_ONE
        elif engine_count >= len(BROWSERS_PROVIDING_CURRENT_ENGINES):
            engines_class_name = ENGINES_CLASS_ALL
            engines_text = IN_ALL

        if mdn_support is None:
            continue

        if engine_count != 2:
            mdn_feature.append_child(E("p", ["class", engines_class_name], [T(engines_text)]))

        support_table = E("div", ["class", "support"])
        mdn_feature.append_child(support_table)

        for b_id in BROWSERS_PROVIDING_CURRENT_ENGINES:
            process_browser_data(b_id, mdn_support.get(b_id), support_table)
        support_table.append_child(E("hr"))
        for b_id in BROWSERS_WITH_BORROWED_ENGINES:
            process_browser_data(b_id, mdn_support.get(b_id), support_table)
        support_table.append_child(E("hr"))
        for b_id in BROWSERS_WITH_RETIRED_ENGINES:
            process_browser_data(b_id, mdn_support.get(b_id), support_table)
        support_table.append_child(E("hr"))
        for b_id in BROWSERS_FOR_MOBILE_DEVICES:
            process_browser_data(b_id, mdn_support.get(b_id), support_table)

        if "caniuse" in mdn_data and isinstance(mdn_data["caniuse"], dict):
            support_table.append_child(E("hr"))
            caniuse_row = E("span", ["data-x", "", "class", "caniuse"])
            caniuse_row.append_child(E("span", ["data-x", ""], [
                E("a", ["href", CAN_I_USE_URL_BASE + str(mdn_data["caniuse"].get("feature", "")), "title", str(mdn_data["caniuse"].get("title", ""))], [T(CAN_I_USE_TEXT)])
            ]))
            support_table.append_child(caniuse_row)


def insert_mdn_annotation_for_element(element: Element, mdn_json_data: dict) -> None:
    if not element.has_attribute("id"):
        return
    elem_id = element.get_attribute("id")
    if elem_id not in mdn_json_data or not isinstance(mdn_json_data[elem_id], list):
        return

    mdn_box = E("div")
    is_first = True

    if element.has_properties(PROP_HEADING) or has_ancestor_with_properties(element, PROP_HEADING):
        class_name = "mdn-anno wrapped"
        mdn_box.set_attribute("class", class_name)
        cand = element
        while not cand.has_properties(PROP_HEADING):
            assert cand.parent_node is not None
            cand = cand.parent_node
        target_ancestor = cand
        next_sibling = target_ancestor.next_element_sibling
        if next_sibling and next_sibling.get_attribute("class") == class_name:
            mdn_box = next_sibling
            is_first = False
        else:
            assert target_ancestor.parent_node is not None
            target_ancestor.parent_node.insert_before(mdn_box, target_ancestor.next_sibling)
            is_first = True
    elif has_ancestor(element, NS_HTML, "td") or has_ancestor(element, NS_HTML, "dt"):
        class_name = "mdn-anno wrapped before"
        cand = element
        while not (isinstance(cand, Element) and (cand.is_identity(NS_HTML, "td") or cand.is_identity(NS_HTML, "dt"))):
            assert cand.parent_node is not None
            cand = cand.parent_node
        target_ancestor = cand
        last_child = target_ancestor.last_element_child
        if last_child and last_child.get_attribute("class") == class_name:
            mdn_box = last_child
            is_first = False
        else:
            target_ancestor.append_child(mdn_box)
            is_first = True
    else:
        class_name = "mdn-anno wrapped before"
        cand = element
        while not (cand.parent_node and isinstance(cand.parent_node, Element) and cand.parent_node.is_identity(NS_HTML, "body")):
            cand = cand.parent_node
        target_ancestor = cand
        prev_sibling = target_ancestor.previous_element_sibling
        if prev_sibling and prev_sibling.get_attribute("class") == class_name:
            mdn_box = prev_sibling
            is_first = False
        else:
            assert target_ancestor.parent_node is not None
            target_ancestor.parent_node.insert_before(mdn_box, target_ancestor)
            is_first = True

    mdn_box.set_attribute("class", class_name)
    add_mdn_box(mdn_box, elem_id, mdn_json_data, is_first)
