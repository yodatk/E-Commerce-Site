import React, {Component} from "react";
import {
    MDBBtn,
    MDBBtnGroup,
    MDBCol,
    MDBContainer,
    MDBInput,
    MDBRow,
    MDBTable,
    MDBTableBody,
    MDBTableHead
} from "mdbreact";
import axios from "axios";
import {Link, Redirect, withRouter} from "react-router-dom";
import FormUtils from "../FormUtils";
import * as HttpStatus from "http-status-codes";

class EditDiscount extends Component {
    state = {
        product_name: "",
        discount_type: "1",
        category: "",
        percent: "",
        free_per_x: "",
        overall_product_quantity: "",
        overall_category_quantity: "",
        overall_product_price: "",
        overall_category_price: "",
        up_to_date: "",
        basket_size: "",
        been_submitted: false,
        errors: FormUtils.defaultAddDiscountDictionary(),
        redirectAfterRegistered: null
    };

    formUtils = new FormUtils();

    validateProductName = () => this.formUtils.validate_product_name_for_adding(this.state.product_name, this.state.errors);

    validatePercent = () => this.formUtils.validate_add_discount_percent(this.state.percent, this.state.errors);

    validateFreePerX = () => this.formUtils.validate_free_per_x(this.state.free_per_x, this.state.errors);

    validateCategory = () => this.formUtils.validate_category_for_adding(this.state.category, this.state.errors);

    validateOverallProductPrice = () => this.formUtils.validate_overall_product_price(this.state.overall_product_price, this.state.errors);
    validateOverallCategoryPrice = () => this.formUtils.validate_overall_category_price(this.state.overall_category_price, this.state.errors);
    validateOverallProductQuantity = () => this.formUtils.validate_overall_product_quantity(this.state.overall_product_quantity, this.state.errors);
    validateOverallCategoryQuantity = () => this.formUtils.validate_overall_category_quantity(this.state.overall_category_quantity, this.state.errors);
    validateUpToDate = () => this.formUtils.validate_up_to_date(this.state.up_to_date, this.state.errors)
    validateBasketSize = () => this.formUtils.validate_basket_size(this.state.basket_size, this.state.errors)

    //
    // componentDidMount() {
    //     this.fetching();
    // }
    //
    // fetching = () => {
    //     axios.get(
    //         "/fetch_discounts",
    //         {
    //             params: {
    //                 user_id: this.props.getUserId(),
    //                 storename: this.props.match.params.storename,
    //                 discount_id: this.props.match.params.discount_id
    //             }
    //         }
    //     )
    //         .then((res) => {
    //             console.log(res)
    //         }).catch(error => {
    //         console.log(error)
    //     });
    // }

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
        this.forceUpdate()
    };

    clearErrors = () => {
        this.setState({errors: FormUtils.defaultAddDiscountDictionary()})
    };

    sendIfPossible = () => {
        if (this.state.errors["is_valid"]) {
            axios.post(
                "/edit_discount",
                {
                    user_id: this.props.getUserId(),
                    discount_id: this.props.match.params.discount_id,
                    storename: this.props.match.params.storename,
                    product_name: this.state.product_name,
                    discount_type: this.state.discount_type,
                    category: this.state.category,
                    percent: this.state.percent,
                    free_per_x: this.state.free_per_x,
                    overall_product_quantity: this.state.overall_product_quantity,
                    overall_category_quantity: this.state.overall_category_quantity,
                    overall_product_price: this.state.overall_product_price,
                    overall_category_price: this.state.overall_category_price,
                    basket_size: this.state.basket_size,
                    up_to_date: this.state.up_to_date,
                },
            )
                .then((res) => {
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
                this.setState({redirectAfterRegistered: '/manage_discounts/'+ this.props.match.params.storename})
            } else {
                this.setState({msg: this.convertErrorToMessage(res.data["error"])})
            }
        }
    }

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ");
            msg = msg.split("_").join(" ");
            return msg;
        }
    };

    onSubmit = (e) => {
        e.preventDefault();
        this.clearErrors();
        let new_errors = null;
        if (this.state.discount_type === "1") {
            new_errors = this.formUtils.validate_new_discount("1/3", this.state.percent, "aaa", this.state.product_name, this.state.overall_product_price, this.state.overall_category_price, this.state.overall_product_quantity, this.state.overall_category_quantity, this.state.up_to_date, this.state.basket_size);
        }
        else if (this.state.discount_type === "2") {
           new_errors = this.formUtils.validate_new_discount(this.state.free_per_x, "50", "aaa", this.state.product_name, this.state.overall_product_price, this.state.overall_category_price, this.state.overall_product_quantity, this.state.overall_category_quantity, this.state.up_to_date, this.state.basket_size);
        }
        else if (this.state.discount_type === "3") {
            new_errors = this.formUtils.validate_new_discount("1/3", this.state.percent, this.state.category, "aaa", this.state.overall_product_price, this.state.overall_category_price, this.state.overall_product_quantity, this.state.overall_category_quantity, this.state.up_to_date, this.state.basket_size);
        }
        else if (this.state.discount_type === "4") {
            new_errors = this.formUtils.validate_new_discount(this.state.free_per_x, "50", this.state.category, "aaa", this.state.overall_product_price, this.state.overall_category_price, this.state.overall_product_quantity, this.state.overall_category_quantity, this.state.up_to_date, this.state.basket_size);
        }
        else {  // type === 5
            new_errors = this.formUtils.validate_new_discount("1/3", this.state.percent, "aaa", "aaa", this.state.overall_product_price, this.state.overall_category_price, this.state.overall_product_quantity, this.state.overall_category_quantity, this.state.up_to_date, this.state.basket_size);
        }
        this.setState({
                been_submitted: true,
                errors: new_errors
            },
            this.sendIfPossible);
    };

    render() {
        if (this.state.redirectAfterRegistered) {
            return <Redirect to={this.state.redirectAfterRegistered}/>
        }

        let product_category = null;
        let percent_freePerX = null;
        if (this.state.discount_type === "1" || this.state.discount_type === "2") {
            this.state.category = ""
            product_category = <div className="grey-text">
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
        } else if (this.state.discount_type !== "5") {
            this.state.product_name = ""
            product_category = <div className="grey-text">
                <div className="form-group">
                    <MDBInput onChange={this.onChange} value={this.state.category}
                              name="category"
                              label="Category" icon="chart-pie" group type="text"
                              className={this.state.been_submitted ? (this.validateCategory() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                              required
                              error="wrong"
                              success="right"/>
                    <div className="invalid-feedback"
                         style={{display: "block"}}>{this.state.errors["category"]}
                    </div>
                    <div className="valid-feedback"/>
                </div>
            </div>
        }
        if (this.state.discount_type === "2" || this.state.discount_type === "4") {
            this.state.percent = ""
            percent_freePerX = <div className="grey-text">
                <div className="form-group">
                    <MDBInput onChange={this.onChange} value={this.state.free_per_x}
                              name="free_per_x"
                              label="FreePerX" icon="star" group type="text"
                              className={this.state.been_submitted ? (this.validateFreePerX() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                              required
                              error="wrong"
                              success="right"/>
                    <div className="invalid-feedback"
                         style={{display: "block"}}>{this.state.errors["free_per_x"]}
                    </div>
                    <div className="valid-feedback"/>
                </div>
            </div>;
        }
        else {
            this.state.free_per_x = ""
            percent_freePerX = <div className="grey-text">
                <div className="form-group">
                    <MDBInput onChange={this.onChange} value={this.state.percent}
                              name="percent"
                              label="Percent" icon="percentage" group type="text"
                              className={this.state.been_submitted ? (this.validatePercent() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                              required
                              error="wrong"
                              success="right"/>
                    <div className="invalid-feedback"
                         style={{display: "block"}}>{this.state.errors["percent"]}
                    </div>
                    <div className="valid-feedback"/>
                </div>
            </div>
        }
        return (
            <MDBContainer>
                <br/>
                <MDBRow
                    style={{
                        display: "flex",
                        alignItems: "right",
                        justifyContent: "right",
                    }}>
                    <MDBCol md="12">
                        <form className="needs-validation" onSubmit={(val) => {
                            this.onSubmit(val)
                        }} noValidate>
                            <p className="h3 text-center mb-4">Edit Discount</p>
                            <div>
                                <select name="discount_type" onChange={this.onChange} value={this.state.discount_type}
                                        className="browser-default custom-select">
                                    <option value="1">Product Discount %</option>
                                    <option value="2">Product Discount FreePerX</option>
                                    <option value="3">Category Discount %</option>
                                    <option value="4">Category Discount FreePerX</option>
                                    <option value="5">Basket discount %</option>
                                </select>
                            </div>
                            {product_category}
                            {percent_freePerX}
                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.overall_category_price}
                                              name="overall_category_price"
                                              label="Overall category price(cat1:am1, cat2:am2)" icon="shekel-sign"
                                              group type="text"
                                              className={this.state.been_submitted ? (this.validateOverallCategoryPrice() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                              required
                                              error="wrong"
                                              success="right"/>
                                    <div className="invalid-feedback"
                                         style={{display: "block"}}>{this.state.errors["overall_category_price"]}
                                    </div>
                                    <div className="valid-feedback"/>
                                </div>
                            </div>
                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.overall_product_price}
                                              name="overall_product_price"
                                              label="Overall product price(prod1:pri1, prod2:pri2)" icon="shekel-sign"
                                              group type="text"
                                              className={this.state.been_submitted ? (this.validateOverallProductPrice() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                              required
                                              error="wrong"
                                              success="right"/>
                                    <div className="invalid-feedback"
                                         style={{display: "block"}}>{this.state.errors["overall_product_price"]}
                                    </div>
                                    <div className="valid-feedback"/>
                                </div>
                            </div>
                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.overall_category_quantity}
                                              name="overall_category_quantity"
                                              label="Overall category quantity(cat1:quan1, cat2:quan2)"
                                              icon="greater-than-equal" group type="text"
                                              className={this.state.been_submitted ? (this.validateOverallCategoryQuantity() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                              required
                                              error="wrong"
                                              success="right"/>
                                    <div className="invalid-feedback"
                                         style={{display: "block"}}>{this.state.errors["overall_category_quantity"]}
                                    </div>
                                    <div className="valid-feedback"/>
                                </div>
                            </div>
                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.overall_product_quantity}
                                              name="overall_product_quantity"
                                              label="Overall product quantity(prod1:quan1, prod2:quan2)"
                                              icon="greater-than-equal" group type="text"
                                              className={this.state.been_submitted ? (this.validateOverallProductQuantity() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                              required
                                              error="wrong"
                                              success="right"/>
                                    <div className="invalid-feedback"
                                         style={{display: "block"}}>{this.state.errors["overall_product_quantity"]}
                                    </div>
                                    <div className="valid-feedback"/>
                                </div>
                            </div>
                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.up_to_date}
                                              name="up_to_date"
                                              label="Up to date (d/m/yyyy)" icon="bell-slash" group type="text"
                                              className={this.state.been_submitted ? (this.validateUpToDate() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                              required
                                              error="wrong"
                                              success="right"/>
                                    <div className="invalid-feedback"
                                         style={{display: "block"}}>{this.state.errors["up_to_date"]}
                                    </div>
                                    <div className="valid-feedback"/>
                                </div>
                            </div>
                            <div className="grey-text">
                                <div className="form-group">
                                    <MDBInput onChange={this.onChange} value={this.state.basket_size}
                                              name="basket_size"
                                              label="Basket size (min items)" icon="shopping-basket" group type="text"
                                              className={this.state.been_submitted ? (this.validateBasketSize() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                              required
                                              error="wrong"
                                              success="right"/>
                                    <div className="invalid-feedback"
                                         style={{display: "block"}}>{this.state.errors["basket_size"]}
                                    </div>
                                    <div className="valid-feedback"/>
                                </div>
                            </div>
                            <div className="text-center">
                                <MDBBtn type="submit"
                                        value="Submit"
                                        outline
                                        id="submit_button"
                                        color="info">Update</MDBBtn>
                            </div>
                        </form>
                        <p onChange={this.onChange} className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                    </MDBCol>
                </MDBRow>
            </MDBContainer>
        );
    }

}

export default withRouter(EditDiscount);
