
##############################################################
##############################################################
############ Parkinson's Disease Analysis Support ############
##############################################################
##############################################################
###################### Author: Lily Sarrafha
###################### Affiliation: Ma'ayan Laboratory
###################### Icahn School of Medicine at Mount Sinai

##############################################################
############# 1. Load libraries
##############################################################

from plotly.offline import init_notebook_mode, iplot
init_notebook_mode()
import sklearn
import matplotlib.pyplot as plt
import numpy as np, seaborn as sns, scipy.stats as ss, plotly.graph_objs as go
from clustergrammer_widget import *
from sklearn.decomposition import PCA
from IPython.display import display, Markdown

##############################################################
############# 2 Prepare functions
##############################################################

def normalize_data(dataframe, filter_genes=True, nr_genes=500): 
    data_log = np.log10(dataframe+1)
    data_norm = data_log / data_log.sum()
    if filter_genes:
        top_genes = data_norm.var(axis=1).sort_values(ascending=False).index.tolist()[:nr_genes]
        data_norm = data_norm.loc[top_genes]
    return data_norm

def generate_figure_legend(figure_number, description):
    display(Markdown('**Figure {figure_number} -** {description}'.format(**locals())))

##############################################################
########## 3. Sample sum values (bar chart)
##############################################################

def sample_barchart(dataframe):
    display(Markdown('**Bar Chart** <br> First, we calculate the sum values for each sample and plot the results in a bar chart.'))
    sample_sum=dataframe.sum(axis=0)
    plt.rcParams['figure.figsize']
    plt.title('Sample Sum Values', fontsize=20)
    plt.xlabel('Samples', fontsize=15)
    plt.ylabel('Sum', fontsize=15)
    sample_sum.plot.bar(figsize=[15,9])

##############################################################
########## 4. Gene median distribution (histogram)
##############################################################

def gene_histogram(dataframe):
    display(Markdown('**Histogram** <br> Then, we calculate the median values for each gene in log scale and plot the results in a histogram.'))
    gene_median=dataframe.median(axis=1)
    np.log10(gene_median+1).plot(kind='hist', bins=50, color='b', log=True, figsize=[15,9])
    plt.rcParams['figure.figsize']
    plt.title('Gene Median Distribution', fontsize=20)
    plt.xlabel('Gene Median', fontsize=15)
    plt.ylabel('Frequency', fontsize=15)

##############################################################
############# 5. 3D PCA plot
##############################################################

def plot_pca_3d(dataframe, size=20, color_by_categorical=None, color_by_continuous=None, colorscale="Viridis", showscale=True, colors=['red', 'blue', 'orange', 'purple', 'turkey', 'chicken', 'thanksigiving']):
    display(Markdown('**3D PCA Plot** <br> We will then normalize the data and calculate the z-score to represent the 500 most variable genes in a 3D PCA plot.'))
    width=900
    height=600
    data_norm = normalize_data(dataframe, filter_genes=True)
    data_zscore=data_norm.apply(ss.zscore, 1)
    pca=PCA(n_components=3)
    pca.fit(data_zscore)
    var_explained = ['PC'+str((i+1))+'('+str(round(e*100, 1))+'% var. explained)' for i, e in enumerate(pca.explained_variance_ratio_)]
    
    if str(color_by_categorical) == 'None':
        if str(color_by_continuous) == 'None':
            marker = dict(size=size)
        else:
            marker = dict(size=size, color=color_by_continuous, colorscale=colorscale, showscale=showscale)
        trace = go.Scatter3d(x=pca.components_[0],
                             y=pca.components_[1],
                             z=pca.components_[2],
                             mode='markers',
                             hoverinfo='text',
                             text=data_zscore.columns,
                             marker=marker)
        data = [trace]
    else:
        # Get unique categories
        unique_categories = color_by_categorical.unique()

        # Define empty list
        data = []
            
        # Loop through the unique categories
        for i, category in enumerate(unique_categories):

            # Get the color corresponding to the category
            category_color = colors[i]

            # Get the indices of the samples corresponding to the category
            category_indices = [i for i, sample_category in enumerate(color_by_categorical) if sample_category == category]
            
            # Create new trace
            trace = go.Scatter3d(x=pca.components_[0][category_indices],
                                 y=pca.components_[1][category_indices],
                                 z=pca.components_[2][category_indices],
                                 mode='markers',
                                 hoverinfo='text',
                                 text=data_zscore.columns,
                                 name = category,
                                 marker=dict(size=size, color=category_color))
            
            # Append trace to data list
            data.append(trace)
    
        
    layout = go.Layout(hovermode='closest',width=width,height=height,scene=dict(xaxis=dict(title=var_explained[0]),
                                                                            yaxis=dict(title=var_explained[1]),
                                                                            zaxis=dict(title=var_explained[2]),
                                                               ),margin=dict(l=0,r=0,b=0,t=0))
    fig = go.Figure(data=data, layout=layout)

    iplot(fig)

##############################################################
########## 6. 2D PCA plot (with color range)
##############################################################

def plot_pca_2d(dataframe, size=30, color=None, colorscale="Viridis", showscale=True):
    display(Markdown('**2D PCA Plot** <br> The same results can be shown in a 2D PCA plot for simplicity.'))
    width=900
    height=600
    data_norm = normalize_data(dataframe, filter_genes=True)
    data_zscore=data_norm.apply(ss.zscore, 1)
    pca = PCA(n_components=2)
    pca.fit(data_zscore)

    if color == None:
        marker = dict(size=size)
    else:
        marker = dict(size=size, color=color, colorscale=colorscale, showscale=showscale)
    
    trace = go.Scatter(
        x = pca.components_[0],
        y = pca.components_[1],
        mode = 'markers',
        hoverinfo='text',
        text=data_zscore.columns,
        marker=marker
    )
    
    fig = dict(data=[trace], layout={})
    fig['layout']['xaxis'] = dict(title='PC1')
    fig['layout']['yaxis'] = dict(title='PC2')
    
    data = [trace]
    iplot(fig)
    display(Markdown('**Figure 4 -** 2D PCA plot of the dataset.'))

##############################################################
############# 7. Clustermap
##############################################################

def plot_clustermap(dataframe, z_score=0, cmap=sns.color_palette("RdBu_r", 500)):
    display(Markdown('**Clustermap** <br> We can also demonstrate the 500 most variable genes in a clustermap.'))
    data_norm = normalize_data(dataframe)
    sns.clustermap(data_norm, z_score=z_score, cmap=cmap)

##############################################################
############# 8. Correlation heatmap
##############################################################

def plot_correlation_heatmap(dataframe, cmap=sns.color_palette("RdBu_r", 500), correlation_axis=0, correlation_method='spearman'):
    display(Markdown('**Gene Co-expression Heatmap** <br> Another method to represent the 500 most variable genes is a correlation heatmap.'))
    data_norm = normalize_data(dataframe, filter_genes=True)

    # correlation
    if correlation_axis:
        dataframe = data_norm.corr(method=correlation_method)
    else:
        dataframe = data_norm.T.corr(method=correlation_method)

    sns.clustermap(dataframe, z_score=None, cmap=cmap)

##############################################################
############# 9. Clustergrammer
##############################################################

def plot_clustergram(dataframe, filter_rows=True, filter_rows_by='var', filter_rows_n=500, normalize=True):
    display(Markdown('**Clustergram** <br> Finally, we will use a clustergram for an interactive mode of demonstrating the data.'))
    data_norm = normalize_data(dataframe)
    net = Network(clustergrammer_widget)
    net.load_df(data_norm)
    net.normalize()
    net.cluster()
    return net.widget()