import React, {Component} from "react";
import {MDBBtn, MDBCol, MDBContainer, MDBIcon, MDBInput, MDBJumbotron, MDBNavLink, MDBRow} from 'mdbreact';
import PropTypes from "prop-types";
import FormUtils from "../FormUtils";
import axios from "axios";
import * as HttpStatus from "http-status-codes"
import {Redirect, withRouter} from "react-router-dom";
import {OK} from "http-status-codes";


class EditProductInStore extends Component {
    state = {
        base_price: "",
        brand: "",
        categories: "",
        been_submitted: false,
        description: "",
        quantity: "",
        errors: FormUtils.defaultEditProductDictionary(),
        redirectAfterRegistered: null,
        msg: ""


    };
    formUtils = new FormUtils();

    validateBrand = () => this.formUtils.validate_brand_for_adding(this.state.brand, this.state.errors);

    validateQuantity = () => this.formUtils.validate_positive_number(this.state.quantity, this.state.errors, "quantity", "Must be Positive")
    validatePrice = () => this.formUtils.validate_positive_number(this.state.price, this.state.errors, "base_price", "Must be Positive")

    validateCategories = () => this.formUtils.validate_categories_for_adding(this.state.categories, this.state.errors);

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
    };

    componentDidMount() {
        let product_name = this.props.match.params.product_name
        let store_name = this.props.match.params.storename
        let user_id = this.props.getUserId()
        axios.get(
            `/get_product_info_view`,
            {
                params: {
                    user_id: user_id,
                    store_name: store_name.trim(),
                    product_name: product_name.trim()
                }
            }
        )
            .then((res) => {
                console.log(res)
                this.dealWithProductResult(res);
            }).catch(error => {
            console.log(error)
            this.dealWithProductResult(error.response);
        });
    }

    dealWithProductResult = (res) => {
        if (res) {
            console.log(res)
            if (res.status === OK) {
                let search_result = res.data["product_info"]
                this.setState({
                    base_price: search_result["price"],
                    quantity: search_result["quantity"],
                    brand: search_result["product"]["brand"],
                    description: search_result["product"]["description"],
                    categories: search_result["product"]["categories"].reduce((acc, curr) => {
                        if (acc === "") {
                            return curr;
                        } else {
                            return `${acc},${curr}`
                        }
                    }, ""),
                })
            }
        }

    }

    onPriceChange = (e) => {
        if (e.target.value > 0)
            this.setState({[e.target.name]: e.target.value})
    };

    clearErrors = () => {
        this.setState({errors: FormUtils.defaultEditProductDictionary()})
    }

    sendIfPossible = () => {
        if (this.state.errors["is_valid"]) {
            axios.post(
                "/edit_product",
                {
                    user_id: this.props.getUserId(),
                    storename: this.props.match.params.storename,
                    product_name: this.props.match.params.product_name,
                    brand: this.state.brand,
                    new_price: this.state.base_price,
                    categories: this.state.categories,
                    description: this.state.description,
                    quantity: this.state.quantity
                },
            )
                .then((res) => {
                    console.log("after post")
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
                console.log("status ok - edit product");
                // register successful
                this.setState({redirectAfterRegistered: '/manage_inventory/' + this.props.match.params.storename})
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
    }


    onSubmit = (e) => {
        e.preventDefault();
        console.log("on submit func")
        this.clearErrors();
        let new_errors = this.formUtils.validate_edit_product(this.state.brand, this.state.categories);
        this.setState({
                been_submitted: true,
                errors: new_errors
            },
            this.sendIfPossible);

    };


    render() {
        if (this.state.redirectAfterRegistered) {
            return <Redirect to={this.state.redirectAfterRegistered}/>
        } else {
            return (
                <React.Fragment>
                    <MDBContainer className="mt-5 text-center">
                        <MDBRow style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                        }}>
                            <MDBCol>
                                <MDBJumbotron>
                                    <h2 className="h2 display-3">{this.props.match.params.product_name}</h2>
                                    <hr className="my-2"/>
                                    <h6 className="lead">
                                        <MDBNavLink
                                            to={`/store_page/${this.props.match.params.storename}`}> Store: {this.props.match.params.storename}</MDBNavLink>
                                    </h6>
                                    <hr className="my-2"/>
                                    <form className="needs-validation" onSubmit={(val) => {
                                        this.onSubmit(val)
                                    }} noValidate>
                                        <div className="grey-text">
                                            <div className="form-group">
                                                <MDBInput onChange={this.onChange} value={this.state.base_price}
                                                          name="base_price"
                                                          label="Base Price" icon="money-bill-wave" group type="number"
                                                          className={this.state.been_submitted ? (this.validatePrice() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                          required
                                                          error="wrong"
                                                          success="right"/>
                                            </div>
                                        </div>
                                        <div className="grey-text">
                                            <div className="form-group">
                                                <MDBInput onChange={this.onChange} value={this.state.quantity}
                                                          name="quantity"
                                                          label="Quantity" icon="list" group type="number"
                                                          className={this.state.been_submitted ? (this.validateQuantity() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
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
                                                    color="info">Edit</MDBBtn>
                                        </div>

                                    </form>
                                </MDBJumbotron>
                                <p onChange={this.onChange}
                                   className="h4 text-center mb-4 text-danger">{this.state.msg}</p>
                            </MDBCol>
                        </MDBRow>
                    </MDBContainer>
                </React.Fragment>
            );
        }
    }
}

// PropTypes
EditProductInStore.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,

};

export default withRouter(EditProductInStore);

