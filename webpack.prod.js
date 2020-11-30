const path = require('path');
const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
    mode: 'production',
    optimization: {
        moduleIds: 'hashed'
    },
    output: {
        filename: '[contenthash].js',
        path: path.resolve(__dirname, 'dst/static/'),
        publicPath: "/"
    }

});
