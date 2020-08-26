const path = require('path');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const RobotstxtPlugin = require("robotstxt-webpack-plugin");
const ImageminWebpWebpackPlugin= require("imagemin-webp-webpack-plugin");

const isDevelopment = process.env.NODE_ENV === 'development'

module.exports = {
    entry: {
        app: './src/index.js'
    },
    performance: {
        hints: 'error',
        maxAssetSize: 4000000
    },
    plugins: [
        new CleanWebpackPlugin(),
        new ImageminWebpWebpackPlugin({
            config: [{
                test: /\.(jpe?g|png)/,
                options: {
                    quality:  75
                }
            }],
            overrideExtension: true,
            detailedLogs: false,
            silent: false,
            strict: true
        }),
        new ManifestPlugin(),
        new RobotstxtPlugin(),
        new MiniCssExtractPlugin({
            filename: isDevelopment ? '[name].css' : 'css/[hash].css',
            chunkFilename: isDevelopment ? '[id].css' : 'css/[hash].css'
        }),
        new HtmlWebpackPlugin({
            favicon: 'src/img/favicon.ico',
            template: "src/index.html",
            compile: true,
            inject: false
        })
    ],
    module: {
        rules: [
            {
                test: /\.module\.s(a|c)ss$/,
                loader: [
                    isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
                    {
                        loader: 'css-loader',
                        options: {
                            modules: true,
                            sourceMap: isDevelopment
                        }
                    },
                    {
                        loader: 'sass-loader',
                        options: {
                            sourceMap: isDevelopment
                        }
                    }
                ]
            },
            {
                test: /\.s(a|c)ss$/,
                exclude: /\.module.(s(a|c)ss)$/,
                loader: [
                    isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
                    'css-loader',
                    {
                        loader: 'sass-loader',
                        options: {
                            sourceMap: isDevelopment
                        }
                    }
                ]
            },
            {
                test: /\.(ico)$/,
                use: [
                    'file-loader',
                ],
            },
            {
                test: /\.(jpe?g|png|gif)$/,
                loader: 'url-loader',
                options: {
                    // Images larger than 10 KB won’t be inlined
                    limit: 20 * 1024,
                    name: 'img/[hash].[ext]',
                }
            },
        ],
    },
    resolve: {
        extensions: ['.js', '.jsx', '.scss']
    }
};