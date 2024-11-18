const ogs = require('open-graph-scraper');
const fs = require('fs'); // To save data to a file

// Get the URL passed as an argument or use a default URL
const url = process.argv[2] ; 

const options = { url };

ogs(options)
  .then((data) => {
    const { error, html, result, response } = data;

    // Log the data
    console.log('Saving JSON...');

    // Save the result to a JSON file
    const jsonData = {
      // error: error,
      // html: html,
      result: result,
      response: response
    };

    fs.writeFileSync('open_graph_data.json', JSON.stringify(jsonData, null, 2), 'utf-8');
  })
  .catch((err) => {
    console.error('Error fetching Open Graph data:', err);
  });
