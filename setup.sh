mkdir -p ~/.streamlit/

echo "\
[server]\n\
porter = $PORT\n\
enableCORS = false\n\
headless = true\n\
\n\
" > ~/.streamlit/config.toml