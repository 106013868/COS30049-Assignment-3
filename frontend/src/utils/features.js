// Friendly names for the model's features, split into two groups for Chart 1.
export const FEATURE_GROUPS = {
  lengths: [
    ["url_length", "Whole URL"],
    ["domain_length", "Domain"],
    ["path_length", "Path"],
  ],
  counts: [
    ["digit_count", "Digits"],
    ["special_character_count", "Symbols"],
    ["dot_count", "Dots"],
    ["subdomain_count", "Subdomains"],
    ["has_ip", "IP address (1 = yes)"],
    ["suspicious_keyword_count", "Suspicious words"],
  ],
};