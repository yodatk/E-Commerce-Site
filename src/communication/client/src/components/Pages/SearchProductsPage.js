import React, {Component} from "react";
import {
    MDBBtn,
    MDBCol,
    MDBContainer,
    MDBIcon,
    MDBInput,
    MDBNavLink,
    MDBRow, MDBTable,
    MDBTableBody,
    MDBTableHead
} from "mdbreact";
import FormUtils from "../FormUtils";
import {Button} from "semantic-ui-react";
import axios from "axios";
import * as HttpStatus from "http-status-codes";
import PropTypes from "prop-types";
import SearchStoresPage from "./SearchStoresPage";

export class SearchProductsPage extends Component {
    state = {
        categories: "",
        product_name: "",
        stores_names: "",
        min_price: 0,
        max_price: 100,
        brands: "",
        been_submitted: false,
        search_result: [],
        msg: "",
        errors: FormUtils.defaultSearchProductDictionary()
    };

    formUtils = new FormUtils();

    validateProductName = () => this.formUtils.validate_productName_for_search(this.state.product_name, this.state.errors);

    columns = [
        {
            label: '#',
            field: 'id',
            sort: 'asc'
        },
        {
            label: 'Product name',
            field: 'name',
            sort: 'asc'
        },
        {
            label: 'Store name',
            field: 'store_name',
            sort: 'asc'
        },
        {
            label: 'Price',
            field: 'price',
            sort: 'asc'
        },
        {
            label: 'Quantity',
            field: 'quantity',
            sort: 'asc'
        },
        {
            label: 'Brand',
            field: 'brand',
            sort: 'asc'
        },
        {
            label: 'Categories',
            field: 'categories',
            sort: 'asc'
        },
        {
            label: 'Link',
            field: 'link',
            sort: 'asc'
        }];


    sendIfPossible = () => {
        if (this.state.errors["is_valid"]) {
            axios.get(
                '/search_products',
                {
                    params: {
                        user_id: this.props.getUserId.bind(this)(),
                        product_name: this.state.product_name,
                        stores_names: this.state.stores_names,
                        categories: this.state.categories,
                        brands: this.state.brands,
                        min_price: this.state.min_price,
                        max_price: this.state.max_price
                    }
                },
            )
                .then((res) => {
                    console.log(res)
                    this.dealWithSearchProductResult(res);
                }).catch(error => {
                console.log(error)
                this.dealWithSearchProductResult(error.response);
            });
        }
    };

    updateSearchResults = (res) => {
        this.setState({search_result: res.data["products"]})
    }

    dealWithSearchProductResult = (res) => {
        if (res) {
            if (res.status === HttpStatus.OK) {
                this.updateSearchResults(res);
                if (this.props.getUserId.bind(this) === -1) {
                    this.props.updateParent.bind(this, {userId: res.data['user_id']})
                }
            } else {
                this.setState({msg: this.convertErrorToMessage(res.data["error"])})
            }
        }
    }

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ")
            msg = msg.split("_").join(" ");
            return msg;
        }
    };

    // validate types of input
    handleNewSearchProduct = () => {
        this.clearErrors();
        let new_errors = this.formUtils.validate_search_products(this.state.categories, this.state.product_name,
            this.state.stores_names, this.state.brands, this.state.min_price, this.state.max_price);
        console.log(new_errors);
        this.setState({
                been_submitted: true,
                errors: new_errors
            },
            this.sendIfPossible);


    }

    onSubmit = (e) => {
        e.preventDefault();
        this.handleNewSearchProduct();
    };

    onPriceChange = (e) => {
        if (e.target.value >= 0)
            this.setState({[e.target.name]: e.target.value})
    };

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
    };

    clearErrors = () => {
        this.setState({errors: FormUtils.defaultSearchProductDictionary()})
    }

    updatedRows = () => {
        let res = [];
        let idCounter = 1;
        for (let item of this.state.search_result) {
            let dictInfo = {};
            dictInfo['id'] = idCounter;

            dictInfo['name'] =
                <MDBNavLink to={`/view_product/${item.product['product']['name']}/${item.product['store_name']}`}>
                    {item.product['product']['name']}</MDBNavLink>;

            dictInfo['store_name'] = <MDBNavLink
                to={`/store_page/${item.product['store_name']}`}>{item.product['store_name']}</MDBNavLink>
            dictInfo['price'] = item.product['after_discount'];
            dictInfo['quantity'] = item.product['quantity'];
            dictInfo['brand'] = item.product['product']['brand'];
            dictInfo['categories'] = item.product['product']['categories'];
            dictInfo['link'] =
                <MDBNavLink to={`/view_product/${item.product['product']['name']}/${item.product['store_name']}`}>
                    <MDBIcon icon="store"/></MDBNavLink>;
            res.push(dictInfo);
            idCounter++;
        }
        return res;
    }

    renderProductsResults = () => {
        // if (!this.state.been_submitted) {
        //     this.setState({product_name: ""}, this.handleNewSearchProduct)
        // }
        return <MDBContainer>
            <MDBTable responsive>
                <MDBTableHead color="default-color" columns={this.columns} textWhite/>
                <MDBTableBody rows={this.updatedRows()}/>
            </MDBTable>
        </MDBContainer>
    }

    render() {
        return (
            <MDBContainer>
                <MDBRow
                    style={{
                        display: "flex",
                        alignItems: "right",
                        justifyContent: "right",
                    }}>
                    <MDBCol md="2">
                        <form className="needs-validation"  onSubmit={(val) => {
                            this.onSubmit(val)}}  noValidate>
                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.categories}
                                              name="categories"
                                              label="Categories" icon="folder" group type="text"
                                              required
                                              error="wrong"
                                              success="right"/>
                                              <div className="invalid-feedback"
                                         style={{display: "block"}}>{this.state.errors["categories"]}</div>
                                    <div className="valid-feedback"/>
                                </div>
                            </div>

                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.product_name}
                                              name="product_name"
                                              label="Product Name" icon="box" group type="text"
                                        className={this.state.been_submitted ? (this.validateProductName() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                              required
                                              error="wrong"
                                              success="right"/>
                                    <div className="invalid-feedback"
                                         style={{display: "block"}}>{this.state.errors["product_name"]}</div>
                                    <div className="valid-feedback"/>
                                </div>
                            </div>

                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.stores_names}
                                              name="stores_names"
                                              label="Stores Names" icon="store" group type="text"
                                              required
                                              error="wrong"
                                              success="right"/>
                                              <div className="invalid-feedback"
                                         style={{display: "block"}}>{this.state.errors["stores_names"]}</div>
                                    <div className="valid-feedback"/>
                                </div>
                            </div>

                            <p>Min Price</p>
                            <div className="grey-text">
                                <div className="def-number-input number-input">
                                    <MDBInput onChange={this.onPriceChange} value={this.state.min_price}
                                              name="min_price" icon="coins"
                                              className="quantity"
                                              type="number"
                                              required
                                              error="wrong"
                                              success="right"/>
                                </div>
                            </div>

                            <p>Max Price</p>
                            <div className="grey-text">
                                <div className="def-number-input number-input">
                                    <MDBInput onChange={this.onPriceChange} value={this.state.max_price}
                                              name="max_price" icon="coins"
                                              className="quantity"
                                              type="number"
                                              required
                                              error="wrong"
                                              success="right"/>
                                </div>
                            </div>

                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.brands}
                                              name="brands"
                                              label="Brands" icon="bold" group type="text"
                                              required
                                              error="wrong"
                                              success="right"/>
                                              <div className="invalid-feedback"
                                         style={{display: "block"}}>{this.state.errors["brands"]}</div>
                                </div>
                            </div>
                            <div className="text-center">
                                        <MDBBtn type="submit"
                                                value="Submit"
                                                outline
                                                color="info">Search</MDBBtn>
                                    </div>
                        </form>
                        <p onChange={this.onChange}
                               className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                    </MDBCol>
                    <MDBCol>
                        {this.renderProductsResults()}
                    </MDBCol>
                </MDBRow>
            </MDBContainer>
        );
    }
}

// PropTypes
SearchProductsPage.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserId: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,
};

export default SearchProductsPage;