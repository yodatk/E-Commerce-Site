import React, {Component} from "react";
import {
    MDBBadge,
    MDBBtn, MDBBtnGroup,
    MDBCol,
    MDBContainer, MDBIcon,
    MDBInput,
    MDBLink, MDBNavLink,
    MDBRow,
    MDBTable,
    MDBTableBody,
    MDBTableHead
} from "mdbreact";
import axios from "axios";
import {Button} from "semantic-ui-react";
import {Link, withRouter} from "react-router-dom";
import {StorePage} from "./StorePage";
import FormUtils from "../FormUtils";
import * as HttpStatus from "http-status-codes";

class ManageInventoryStore extends Component {
    state = {
        products: [],
        product_name: "",
        base_price: "",
        quantity: 1,
        brand: "",
        categories: "",
        description: "",
        been_submitted: false,
        errors: FormUtils.defaultAddProductDictionary()
    };

    formUtils = new FormUtils();

    validateProductName = () => this.formUtils.validate_product_name_for_adding(this.state.product_name, this.state.errors);

    validateBrand = () => this.formUtils.validate_brand_for_adding(this.state.brand, this.state.errors);

    validateCategories = () => this.formUtils.validate_categories_for_adding(this.state.categories, this.state.errors);


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
            label: 'Description',
            field: 'description',
            sort: 'asc'
        },
        {
            label: 'Edit',
            field: 'edit',
            sort: 'asc'
        }
    ];


    componentDidMount() {
        this.fetching();
    }

    fetching = () => {

        axios.get(
            "/fetch_products_of_store",
            {
                params: {
                    user_id: this.props.getUserId(),
                    storename: this.props.match.params.storename
                }
            }
        )
            .then((res) => {
                this.setState({products: res.data !== null && 'products' in res.data ? res.data.products : []});
                console.log(this.state.products)
            }).catch(error => {
            console.log(error)
        });
    }

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
    };

    onPriceChange = (e) => {
        if (e.target.value > 0)
            this.setState({[e.target.name]: e.target.value})
    };

    clearErrors = () => {
        this.setState({errors: FormUtils.defaultAddProductDictionary()})
    }
    sendIfPossible = () => {
        if (this.state.errors["is_valid"]) {
            axios.post(
                "/add_product_to_store",
                {
                    user_id: this.props.getUserId(),
                    storename: this.props.match.params.storename,
                    product_name: this.state.product_name,
                    base_price: this.state.base_price,
                    quantity: this.state.quantity,
                    categories: this.state.categories,
                    brand: this.state.brand,
                    description: this.state.description
                },
            )
                .then((res) => {
                    console.log('Product added', res)
                    this.dealWithRegisterResult(res);
                }).catch(error => {
                console.log(error)
                this.dealWithRegisterResult(error.response);
            });
        }
    }

    dealWithRegisterResult = (res) => {
        if (res) {
            if (res.status === HttpStatus.OK) {
                console.log("ok status");
                this.fetching()
            } else {
                this.setState({msg: this.convertErrorToMessage(res.data["error"])})
            }
        }

    };

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ");
            msg = msg.split("_").join(" ");
            return msg;
        }
    };

    delete_product = (product_name) => {
        if (window.confirm("Are you sure?")) {
            console.log('Say yes');
            axios.post(
                "/remove_product",
                {
                    user_id: this.props.getUserId(),
                    storename: this.props.match.params.storename,
                    product_name: product_name
                },
            )
                .then((res) => {
                    console.log('Product removed', res);
                    this.dealWithRegisterResult(res);
                }).catch(error => {
                console.log(error);
                this.dealWithRegisterResult(error.response);
            });
        } else {
            console.log('Say no')
        }
    };

    onSubmit = (e) => {
        e.preventDefault();
        console.log("on submit func")
        this.clearErrors();
        let new_errors = this.formUtils.validate_new_product(this.state.product_name, this.state.brand, this.state.categories);
        this.setState({
                been_submitted: true,
                errors: new_errors
            },
            this.sendIfPossible);

    };
    updatedRows = () => {
        let res = [];
        let idCounter = 1;
        for (let product of this.state.products) {
            let dictInfo = {};
            dictInfo['id'] = idCounter;
            dictInfo['name'] = product['name'];
            dictInfo['price'] = product['price'];
            dictInfo['quantity'] = product['quantity'];
            dictInfo['brand'] = product['brand'];
            dictInfo['categories'] = product['categories'];
            dictInfo['description'] = product['description'];
            dictInfo['edit'] =
                <div>
                    <MDBBtnGroup size="md">
                        <MDBBtn color="warning" id="delete_button" onClick={() => {
                            this.delete_product(dictInfo['name'])
                        }}>Delete Product</MDBBtn>
                    </MDBBtnGroup>
                    <MDBBtnGroup size="md">
                        <MDBBtn color="primary"><Link style={{'color': 'white'}}
                                                      to={`/edit_product/${dictInfo['name']}/${this.props.match.params.storename}`}>Edit
                            Product</Link></MDBBtn>
                    </MDBBtnGroup>
                </div>;

            res.push(dictInfo);
            idCounter++;
        }
        return res;
    };

    renderProductsResults = () => {
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
                <br/>
                <MDBRow
                    style={{
                        display: "flex",
                        alignItems: "right",
                        justifyContent: "right",
                    }}>
                    <MDBCol md="3">
                        <form className="needs-validation" onSubmit={(val) => {
                            this.onSubmit(val)
                        }} noValidate>
                            <p className="h3 text-center mb-4">Add Product</p>
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
                                         style={{display: "block"}}>{this.state.errors["product_name"]}
                                    </div>
                                    <div className="valid-feedback"/>
                                </div>
                            </div>

                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.base_price}
                                              name="base_price"
                                              label="Base Price" icon="money-bill-wave" group type="number"
                                              required
                                              error="wrong"
                                              success="right"/>
                                </div>
                            </div>

                            <div className="grey-text">
                                <div className="def-number-input number-input">
                                    <MDBInput onChange={this.onPriceChange} value={this.state.quantity}
                                              name="quantity" icon="list" label="Quantity"
                                              className="quantity"
                                              type="number"
                                              required
                                              error="wrong"
                                              success="right"/>
                                </div>
                            </div>

                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.brand}
                                              name="brand"
                                              label="Brands" icon="bold" group type="text"
                                              className={this.state.been_submitted ? (this.validateBrand() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                              required
                                              error="wrong"
                                              success="right"/>
                                </div>
                            </div>
                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.categories}
                                              name="categories"
                                              label="Categories" icon="folder" group type="text"
                                              className={this.state.been_submitted ? (this.validateCategories() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                              required
                                              error="wrong"
                                              success="right"/>
                                </div>
                            </div>
                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.description}
                                              name="description"
                                              label="Description" icon="align-left" group type="text"
                                              className={this.state.been_submitted ? "form-control is-valid" : 'form-control'}
                                              required
                                              error="wrong"
                                              success="right"/>
                                </div>
                            </div>
                            <div className="text-center">
                                <MDBBtn type="submit"
                                        value="Submit"
                                        outline
                                        id="submit_button"
                                        color="info">Add</MDBBtn>
                            </div>
                        </form>
                        <p onChange={this.onChange} className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                    </MDBCol>
                    <MDBCol>
                        {this.renderProductsResults()}
                    </MDBCol>
                </MDBRow>


            </MDBContainer>
        );
    }
}

export default withRouter(ManageInventoryStore);
